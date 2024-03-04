import os

from boto3.dynamodb.conditions import Key
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class UploadConfirmResultService:
    def __init__(self):
        self.dynamo_service = DynamoDBService()
        self.s3_service = S3Service()

    def process_documents(self, nhs_number, documents: dict):
        lg_table_name = os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]
        lg_bucket_name = os.environ["LLOYD_GEORGE_BUCKET_NAME"]
        arf_bucket_name = os.environ["DOCUMENT_STORE_BUCKET_NAME"]
        arf_table_name = os.environ["DOCUMENT_STORE_DYNAMODB_NAME"]
        arf_document_references: list[str] = documents.get("ARF")
        lg_document_references: list[str] = documents.get("LG")

        if arf_document_references:
            self.copy_files_from_staging_bucket(
                arf_document_references, arf_bucket_name, nhs_number
            )
            self.delete_files_from_staging_bucket(
                arf_document_references, arf_bucket_name
            )
            self.update_dynamo_table(arf_table_name, arf_document_references)

        if lg_document_references:
            self.validate_number_of_documents(
                lg_table_name, nhs_number, lg_document_references
            )
            self.copy_files_from_staging_bucket(
                lg_document_references, lg_bucket_name, nhs_number
            )
            self.delete_files_from_staging_bucket(
                lg_document_references, lg_bucket_name
            )
            self.update_dynamo_table(lg_table_name, lg_document_references)

    # return 204 if all files processed successfully

    def copy_files_from_staging_bucket(
        self, document_references: list, bucket_name: str, nhs_number: str
    ):
        staging_bucket = os.environ["STAGING_BUCKET"]

        for document_reference in document_references:
            dest_file_key = f"{nhs_number}/{document_reference}"

            self.s3_service.copy_across_bucket(
                source_bucket=staging_bucket,
                source_file_key=document_reference,
                dest_bucket=bucket_name,
                dest_file_key=dest_file_key,
            )

    def delete_files_from_staging_bucket(
        self, document_references: list, bucket_name: str
    ):
        for document_reference in document_references:
            self.s3_service.delete_object(bucket_name, document_reference)

    def update_dynamo_table(self, table_name: str, document_references: list[str]):
        for reference in document_references:
            self.dynamo_service.update_item(table_name, reference, {"Uploaded": True})

    def validate_number_of_documents(
        self, table_name: str, nhs_number, document_references: list
    ):
        query_response = self.dynamo_service.simple_query(
            table_name=table_name,
            key_condition_expression=Key("NhsNumber").eq(nhs_number),
        )

        return len(query_response["Items"]) == len(document_references)
