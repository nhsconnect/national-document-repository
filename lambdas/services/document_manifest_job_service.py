import itertools
import os

from enums.lambda_error import LambdaError
from enums.supported_document_types import SupportedDocumentTypes
from enums.zip_trace import ZipTraceStatus
from models.document_reference import DocumentReference
from models.zip_trace import DocumentManifestJob, DocumentManifestZipTrace
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from services.document_service import DocumentService
from utils.audit_logging_setup import LoggingService
from utils.common_query_filters import UploadCompleted
from utils.lambda_exceptions import DocumentManifestJobServiceException

logger = LoggingService(__name__)


class DocumentManifestJobService:
    def __init__(self):
        create_document_aws_role_arn = os.getenv("PRESIGNED_ASSUME_ROLE")
        self.s3_service = S3Service(custom_aws_role=create_document_aws_role_arn)
        self.document_service = DocumentService()
        self.dynamo_service = DynamoDBService()
        self.zip_output_bucket = os.environ["ZIPPED_STORE_BUCKET_NAME"]
        self.zip_trace_table = os.environ["ZIPPED_STORE_DYNAMODB_NAME"]
        self.documents: list[DocumentReference] = []

    def create_document_manifest_job(
        self,
        nhs_number: str,
        doc_types: list[SupportedDocumentTypes],
        selected_document_references: list[str] = None,
    ) -> str:
        logger.info("Retrieving Document References for manifest")

        self.documents = list(
            itertools.chain.from_iterable(
                [
                    self.document_service.fetch_available_document_references_by_type(
                        nhs_number=nhs_number,
                        doc_type=doc_type,
                        query_filter=UploadCompleted,
                    )
                    for doc_type in doc_types
                ]
            )
        )

        if not self.documents:
            raise DocumentManifestJobServiceException(404, LambdaError.ManifestNoDocs)

        if selected_document_references:
            self.documents = self.filter_documents_by_reference(
                selected_document_references=selected_document_references,
            )

        documents_to_download = {
            document.file_location: document.file_name
            for document in self.handle_duplicate_document_filenames()
        }

        job_id = self.write_zip_trace(documents_to_download)

        return job_id

    def filter_documents_by_reference(
        self,
        selected_document_references: list[str],
    ) -> list[DocumentReference]:
        logger.info("Filtering Selected Document References for manifest")

        reference_set = set(selected_document_references)
        matched_references = [
            document_reference
            for document_reference in self.documents
            if document_reference.id in reference_set
        ]

        if not matched_references:
            raise DocumentManifestJobServiceException(
                400, LambdaError.ManifestFilterDocumentReferences
            )

        return matched_references

    def handle_duplicate_document_filenames(self) -> list[DocumentReference]:
        file_names_to_be_zipped = {}

        for document in self.documents:
            file_name = document.file_name
            duplicated_filename = file_name in file_names_to_be_zipped

            if duplicated_filename:
                file_names_to_be_zipped[file_name] += 1
                document.file_name = document.create_unique_filename(
                    file_names_to_be_zipped[file_name]
                )
            else:
                file_names_to_be_zipped[file_name] = 1

        return self.documents

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

    def create_document_manifest_presigned_url(
        self, job_id: str
    ) -> DocumentManifestJob:
        zip_trace = self.query_zip_trace(job_id=job_id)

        match zip_trace.job_status:
            case ZipTraceStatus.PENDING:
                return DocumentManifestJob(jobStatus=ZipTraceStatus.PENDING, url="")
            case ZipTraceStatus.PROCESSING:
                return DocumentManifestJob(jobStatus=ZipTraceStatus.PROCESSING, url="")
            case ZipTraceStatus.COMPLETED:
                is_manifest_ready = self.s3_service.file_exist_on_s3(
                    self.zip_output_bucket, zip_trace.zip_file_location
                )
                if not is_manifest_ready:
                    raise DocumentManifestJobServiceException(
                        404, LambdaError.ManifestMissingJob
                    )
                presigned_url = self.s3_service.create_download_presigned_url(
                    s3_bucket_name=self.zip_output_bucket,
                    file_key=zip_trace.zip_file_location,
                )
                return DocumentManifestJob(
                    jobStatus=ZipTraceStatus.COMPLETED, url=presigned_url
                )

    def query_zip_trace(self, job_id: str) -> DocumentManifestZipTrace:
        response = self.dynamo_service.query_with_requested_fields(
            table_name=self.zip_trace_table,
            index_name="JobIdIndex",
            search_key="JobId",
            search_condition=job_id,
            requested_fields=list(DocumentManifestZipTrace.model_fields.keys()),
        )
        if not response["Items"]:
            raise DocumentManifestJobServiceException(
                404, LambdaError.ManifestMissingJob
            )

        return DocumentManifestZipTrace.model_validate(response["Items"][0])
