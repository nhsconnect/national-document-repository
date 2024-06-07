import os
import shutil
import tempfile
import zipfile

from botocore.exceptions import ClientError
from enums.dynamo_filter import AttributeOperator, ConditionOperator
from enums.lambda_error import LambdaError
from enums.metadata_field_names import DocumentReferenceMetadataFields
from enums.supported_document_types import SupportedDocumentTypes
from models.document_reference import DocumentReference
from models.zip_trace import ZipTrace
from pydantic import ValidationError
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from services.document_service import DocumentService
from utils.audit_logging_setup import LoggingService
from utils.common_query_filters import UploadCompleted
from utils.dynamo_query_filter_builder import DynamoQueryFilterBuilder
from utils.exceptions import DynamoServiceException
from utils.lambda_exceptions import DocumentManifestServiceException
from utils.lloyd_george_validator import (
    LGInvalidFilesException,
    check_for_number_of_files_match_expected,
)

logger = LoggingService(__name__)


class DocumentManifestService:
    def __init__(self, nhs_number):
        self.nhs_number = nhs_number
        create_document_aws_role_arn = os.getenv("PRE_SIGN_ASSUME_ROLE")
        self.s3_service = S3Service(custom_aws_role=create_document_aws_role_arn)
        self.dynamo_service = DynamoDBService()
        self.document_service = DocumentService()

        self.zip_file_name = f"patient-record-{self.nhs_number}.zip"
        self.temp_downloads_dir = tempfile.mkdtemp()
        self.temp_output_dir = tempfile.mkdtemp()
        self.zip_output_bucket = os.environ["ZIPPED_STORE_BUCKET_NAME"]
        self.zip_trace_table = os.environ["ZIPPED_STORE_DYNAMODB_NAME"]

    def create_document_manifest_presigned_url(
        self,
        document_types: list[SupportedDocumentTypes],
        document_references: list[str] = None,
    ) -> str:
        try:
            documents = self.arrange_documents_for_download(
                document_types, document_references
            )
            if not documents:
                logger.error(
                    f"{LambdaError.ManifestNoDocs.to_str()}",
                    {"Result": "Failed to create document manifest"},
                )
                raise DocumentManifestServiceException(
                    status_code=404, error=LambdaError.ManifestNoDocs
                )
            self.download_documents_to_be_zipped(documents)
            self.upload_zip_file()

            # Removes the parent of each removed directory until the parent does not exist or the parent is not empty
            shutil.rmtree(self.temp_downloads_dir)
            shutil.rmtree(self.temp_output_dir)

            return self.s3_service.create_download_presigned_url(
                s3_bucket_name=self.zip_output_bucket, file_key=self.zip_file_name
            )

        except ValidationError as e:
            logger.error(
                f"{LambdaError.ManifestValidation.to_str()}: {str(e)}",
                {"Result": "Failed to create document manifest"},
            )
            raise DocumentManifestServiceException(
                status_code=500, error=LambdaError.ManifestValidation
            )
        except DynamoServiceException as e:
            logger.error(
                f"{LambdaError.ManifestDB.to_str()}: {str(e)}",
                {"Result": "Failed to create document manifest"},
            )
            raise DocumentManifestServiceException(
                status_code=500, error=LambdaError.ManifestDB
            )
        except LGInvalidFilesException as e:
            logger.error(
                f"{LambdaError.IncompleteRecordError.to_str()}: {str(e)}",
                {"Result": "Failed to create document manifest"},
            )
            raise DocumentManifestServiceException(
                status_code=400, error=LambdaError.IncompleteRecordError
            )

    def arrange_documents_for_download(
        self,
        doc_types: list[SupportedDocumentTypes],
        document_references: list[str] = None,
    ):
        documents = []
        query_filter = UploadCompleted

        if document_references:
            query_filter = (
                query_filter
                & self.create_filter_expression_for_document_references(
                    document_references
                )
            )

        for doc_type in doc_types:
            documents_for_doc_type = self.retrieve_document_metadata_from_dynamo(
                doc_type, query_filter
            )
            if documents_for_doc_type and doc_type == SupportedDocumentTypes.LG:
                check_for_number_of_files_match_expected(
                    documents_for_doc_type[0].file_name, len(documents_for_doc_type)
                )
            documents += documents_for_doc_type
        return documents

    def create_filter_expression_for_document_references(self, document_references):
        dynamo_filter_document_by_references = (
            DynamoQueryFilterBuilder().set_combination_operator(
                operator=ConditionOperator.OR
            )
        )
        for document_reference in document_references:
            dynamo_filter_document_by_references.add_condition(
                attribute=str(DocumentReferenceMetadataFields.ID.value),
                attr_operator=AttributeOperator.EQUAL,
                filter_value=document_reference,
            )
        return dynamo_filter_document_by_references.build()

    def retrieve_document_metadata_from_dynamo(self, doc_type, query_filter):
        return self.document_service.fetch_available_document_references_by_type(
            nhs_number=self.nhs_number,
            doc_type=doc_type,
            query_filter=query_filter,
        )

    def download_documents_to_be_zipped(self, documents: list[DocumentReference]):
        logger.info("Downloading documents to be zipped")
        file_names_to_be_zipped = {}

        for document in documents:
            file_name = document.file_name

            duplicated_filename = file_name in file_names_to_be_zipped

            if duplicated_filename:
                file_names_to_be_zipped[file_name] += 1
                document.file_name = document.create_unique_filename(
                    file_names_to_be_zipped[file_name]
                )

            else:
                file_names_to_be_zipped[file_name] = 1

            download_path = os.path.join(self.temp_downloads_dir, document.file_name)

            try:
                self.s3_service.download_file(
                    document.get_file_bucket(), document.get_file_key(), download_path
                )
            except ClientError as e:
                msg = f"{document.get_file_key()} may reference missing file in s3 bucket: {document.get_file_bucket()}"
                logger.error(
                    f"{LambdaError.ManifestClient.to_str()} {msg + str(e)}",
                    {"Result": "Failed to create document manifest"},
                )
                raise DocumentManifestServiceException(
                    status_code=500, error=LambdaError.ManifestClient
                )

    def upload_zip_file(self):
        logger.info("Creating zip from files")

        zip_file_path = os.path.join(self.temp_output_dir, self.zip_file_name)
        with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(self.temp_downloads_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, self.temp_downloads_dir)
                    zipf.write(file_path, arc_name)

        logger.info("Uploading zip file to s3")
        self.s3_service.upload_file(
            file_name=zip_file_path,
            s3_bucket_name=self.zip_output_bucket,
            file_key=f"{self.zip_file_name}",
        )

        logger.info("Writing zip trace to db")
        zip_trace = ZipTrace(
            f"s3://{self.zip_output_bucket}/{self.zip_file_name}",
        )

        self.dynamo_service.create_item(self.zip_trace_table, zip_trace.to_dict())
