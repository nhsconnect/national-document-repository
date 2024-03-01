import os

from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class UploadConfirmResultService:
    def __init__(self):
        self.dynamo_service = DynamoDBService()
        self.s3_service = S3Service()
        self.staging_bucket = os.environ["STAGING_BUCKET"]

    def process_documents(self, documents: dict):
        lloyd_george_table_name = os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]
        lloyd_george_bucket_name = os.environ["LLOYD_GEORGE_BUCKET_NAME"]
        arf_bucket_name = os.environ["DOCUMENT_STORE_BUCKET_NAME"]
        arf_table_name = os.environ["DOCUMENT_STORE_DYNAMODB_NAME"]
        arf_document_references: list[str] = documents.get("ARF")
        lg_document_references: list[str] = documents.get("LG")

        if arf_document_references:
            self.move_files_from_staging_bucket(
                arf_document_references, arf_bucket_name
            )
            self.update_dynamo_table(arf_table_name, arf_document_references)

        if lg_document_references:
            # validate docs
            self.move_files_from_staging_bucket(
                lg_document_references, lloyd_george_bucket_name
            )
            self.update_dynamo_table(lloyd_george_table_name, lg_document_references)

    # return 204 if all files processed successfully

    def move_files_from_staging_bucket(
        self, document_references: list, bucket_name: str
    ):
        for document_reference in document_references:
            self.s3_service.copy_across_bucket(
                source_bucket=self.staging_bucket,
                source_file_key=document_reference,
                dest_bucket=bucket_name,
                dest_file_key=document_reference,
            )

    def update_dynamo_table(self, table_name: str, document_references: list[str]):
        for reference in document_references:
            self.dynamo_service.update_item(table_name, reference, {"Uploaded": True})
