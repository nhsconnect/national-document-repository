import os
import shutil
import tempfile
import zipfile

from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from enums.supported_document_types import SupportedDocumentTypes
from models.document_reference import DocumentReference
from models.zip_trace import ZipTrace
from pydantic import ValidationError
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from services.document_service import DocumentService
from utils.audit_logging_setup import LoggingService
from utils.common_query_filters import UploadCompleted
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
        self.s3_service = S3Service()
        self.dynamo_service = DynamoDBService()
        self.document_service = DocumentService()

        self.zip_file_name = f"patient-record-{self.nhs_number}.zip"
        self.temp_downloads_dir = tempfile.mkdtemp()
        self.temp_output_dir = tempfile.mkdtemp()
        self.zip_output_bucket = os.environ["ZIPPED_STORE_BUCKET_NAME"]
        self.zip_trace_table = os.environ["ZIPPED_STORE_DYNAMODB_NAME"]

    def create_document_manifest_presigned_url(
        self, doc_type: SupportedDocumentTypes
    ) -> str:
        try:
            documents = (
                self.document_service.fetch_available_document_references_by_type(
                    nhs_number=self.nhs_number,
                    doc_type=doc_type,
                    query_filter=UploadCompleted,
                )
            )

            if not documents:
                logger.error(
                    f"{LambdaError.ManifestNoDocs.to_str()}",
                    {"Result": "Failed to create document manifest"},
                )
                raise DocumentManifestServiceException(
                    status_code=404, error=LambdaError.ManifestNoDocs
                )
            if doc_type == SupportedDocumentTypes.LG:
                check_for_number_of_files_match_expected(
                    documents[0].file_name, len(documents)
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

        self.download_documents_to_be_zipped(documents)
        self.upload_zip_file()

        shutil.rmtree(self.temp_downloads_dir)
        shutil.rmtree(self.temp_output_dir)

        return self.s3_service.create_download_presigned_url(
            s3_bucket_name=self.zip_output_bucket, file_key=self.zip_file_name
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
