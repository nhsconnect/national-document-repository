import os

from enums.virus_scan_result import VirusScanResult
from models.document_reference import DocumentReference
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from services.document_service import DocumentService
from services.virus_scan_result_service import VirusScanService
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class UploadDocumentReferenceService:
    def __init__(self):
        self.staging_s3_bucket_name = os.getenv("STAGING_STORE_BUCKET_NAME")
        self.table_name = os.getenv("LLOYD_GEORGE_DYNAMODB_NAME")
        self.lg_bucket_name = os.getenv("LLOYD_GEORGE_BUCKET_NAME")

        self.document_service = DocumentService()
        self.dynamo_service = DynamoDBService()
        self.virus_scan_service = VirusScanService()
        self.s3_service = S3Service()

    def handle_upload_document_reference_request(self, document_id: str):
        documents = self.document_service.fetch_documents_from_table(
            table=self.table_name,
            search_condition=document_id,
            search_key="ID",
        )
        document_reference = documents[0]
        if not document_reference:
            logger.error(
                f"No document with the following key found in {self.table_name} table: {document_id}"
            )
            logger.info("Skipping this object")

        # comment out call to virus scan, waiting for NDR-98
        # virus_scan_result = self.virus_scan_service.scan_file(
        #     document_reference.s3_file_key
        # )

        virus_scan_result = VirusScanResult.CLEAN
        if virus_scan_result == VirusScanResult.CLEAN:
            document_reference.file_location = self.copy_files_from_staging_bucket(
                document_reference
            )

        self.delete_file_from_staging_bucket(document_reference)
        self.update_dynamo_table(document_reference, virus_scan_result)

    def update_dynamo_table(
        self, document: DocumentReference, scan_result: VirusScanResult
    ):
        logger.info("Updating dynamo db table")
        document.virus_scanner_result = scan_result
        if scan_result == VirusScanResult.INFECTED:
            document.doc_status = "cancelled"
        else:
            document.doc_status = "final"

        self.document_service.update_document(
            table_name=self.table_name,
            document_reference=document,
            update_fields_name={"virus_scan_result", "doc_status", "file_location"},
        )

    def copy_files_from_staging_bucket(self, document_reference: DocumentReference):
        logger.info("Copying files from staging bucket")

        dest_file_key = (
            f"{document_reference.nhs_number}/{document_reference.s3_file_key}"
        )
        source_file_key = document_reference.file_location

        self.s3_service.copy_across_bucket(
            source_bucket=self.staging_s3_bucket_name,
            source_file_key=source_file_key,
            dest_bucket=self.lg_bucket_name,
            dest_file_key=dest_file_key,
        )
        return dest_file_key

    def delete_file_from_staging_bucket(self, document_reference: DocumentReference):
        source_file_key = document_reference.file_location
        self.s3_service.delete_object(self.staging_s3_bucket_name, source_file_key)
