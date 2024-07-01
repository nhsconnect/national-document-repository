import os

from enums.lambda_error import LambdaError
from enums.supported_document_types import SupportedDocumentTypes
from pydantic import ValidationError
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from services.document_service import DocumentService
from utils.audit_logging_setup import LoggingService
from utils.common_query_filters import UploadCompleted
from utils.exceptions import DynamoServiceException
from utils.lambda_exceptions import DocumentManifestServiceException
from utils.lloyd_george_validator import LGInvalidFilesException

logger = LoggingService(__name__)


class DocumentManifestService:
    def __init__(self, nhs_number):
        self.nhs_number = nhs_number
        create_document_aws_role_arn = os.getenv("PRESIGNED_ASSUME_ROLE")
        self.s3_service = S3Service(custom_aws_role=create_document_aws_role_arn)
        self.dynamo_service = DynamoDBService()
        self.document_service = DocumentService()
        self.zip_output_bucket = os.environ["ZIPPED_STORE_BUCKET_NAME"]
        self.zip_file_name = f"patient-record-{self.nhs_number}.zip"

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

        for doc_type in doc_types:
            documents_for_doc_type = self.retrieve_document_metadata_from_dynamo(
                doc_type, query_filter
            )

            for document in documents_for_doc_type:
                if document.id in document_references:
                    documents += document

        return documents

    def retrieve_document_metadata_from_dynamo(self, doc_type, query_filter):
        return self.document_service.fetch_available_document_references_by_type(
            nhs_number=self.nhs_number,
            doc_type=doc_type,
            query_filter=query_filter,
        )
