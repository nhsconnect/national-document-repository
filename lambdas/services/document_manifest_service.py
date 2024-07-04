import itertools
import os
import tempfile

from enums.lambda_error import LambdaError
from enums.supported_document_types import SupportedDocumentTypes
from models.document_reference import DocumentReference
from models.zip_trace import DocumentManifestZipTrace
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from services.document_service import DocumentService
from utils.audit_logging_setup import LoggingService
from utils.common_query_filters import UploadCompleted
from utils.lambda_exceptions import DocumentManifestServiceException

logger = LoggingService(__name__)


class DocumentManifestService:
    def __init__(self, nhs_number):
        self.nhs_number = nhs_number
        create_document_aws_role_arn = os.getenv("PRESIGNED_ASSUME_ROLE")
        self.s3_service = S3Service(custom_aws_role=create_document_aws_role_arn)
        self.dynamo_service = DynamoDBService()
        self.document_service = DocumentService()

        self.zip_file_name = f"patient-record-{self.nhs_number}.zip"
        self.temp_downloads_dir = tempfile.mkdtemp()
        self.temp_output_dir = tempfile.mkdtemp()
        self.zip_output_bucket = os.environ["ZIPPED_STORE_BUCKET_NAME"]
        self.zip_trace_table = os.environ["ZIPPED_STORE_DYNAMODB_NAME"]

    def create_document_manifest_job(
        self,
        doc_types: list[SupportedDocumentTypes],
        selected_document_references: list[str] = None,
    ) -> str:
        logger.info("Retrieving Document References for manifest")

        documents = list(
            itertools.chain.from_iterable(
                [
                    self.document_service.fetch_available_document_references_by_type(
                        nhs_number=self.nhs_number,
                        doc_type=doc_type,
                        query_filter=UploadCompleted,
                    )
                    for doc_type in doc_types
                ]
            )
        )

        if not documents:
            raise DocumentManifestServiceException(404, LambdaError.ManifestNoDocs)

        if selected_document_references:
            documents = self.filter_documents_by_reference(
                documents=documents,
                selected_document_references=selected_document_references,
            )

        documents_to_download = {
            document.file_location: document.file_name
            for document in self.handle_duplicate_document_filenames(documents)
        }

        job_id = self.write_zip_trace(documents_to_download)

        return job_id

    def filter_documents_by_reference(
        self,
        documents: list[DocumentReference],
        selected_document_references: list[str],
    ) -> list[DocumentReference]:
        logger.info("Filtering Selected Document References for manifest")

        reference_set = set(selected_document_references)
        matched_references = [
            document_reference
            for document_reference in documents
            if document_reference.id in reference_set
        ]

        if not matched_references:
            raise DocumentManifestServiceException(
                400, LambdaError.ManifestFilterDocumentReferences
            )

        return matched_references

    def handle_duplicate_document_filenames(
        self, documents: list[DocumentReference]
    ) -> list[DocumentReference]:
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

        return documents

    def write_zip_trace(
        self,
        documents_to_download: dict,
    ) -> str:
        logger.info("Writing Document Manifest zip trace to db")

        zip_trace = DocumentManifestZipTrace(FilesToDownload=documents_to_download)
        self.dynamo_service.create_item(
            self.zip_trace_table, zip_trace.model_dump(by_alias=True)
        )

        return str(zip_trace.job_id)

    def create_document_manifest_presigned_url(self, job_id: str):
        return self.s3_service.create_download_presigned_url(
            s3_bucket_name=self.zip_output_bucket, file_key=self.zip_file_name
        )

    def query_zip_trace(self, job_id: str) -> DocumentManifestZipTrace:
        # zip_trace = self.dynamo_service.query_all_fields()
        pass
