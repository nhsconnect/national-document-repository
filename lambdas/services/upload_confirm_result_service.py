import os

from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from utils.audit_logging_setup import LoggingService
from utils.exceptions import UploadConfirmResultException

logger = LoggingService(__name__)


class UploadConfirmResultService:
    def __init__(self, nhs_number):
        self.dynamo_service = DynamoDBService()
        self.s3_service = S3Service()
        self.nhs_number = nhs_number

    def process_documents(self, documents: dict):
        lg_table_name = os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]
        lg_bucket_name = os.environ["LLOYD_GEORGE_BUCKET_NAME"]
        arf_bucket_name = os.environ["DOCUMENT_STORE_BUCKET_NAME"]
        arf_table_name = os.environ["DOCUMENT_STORE_DYNAMODB_NAME"]
        arf_document_references: list[str] = documents.get("ARF")
        lg_document_references: list[str] = documents.get("LG")

        try:
            if arf_document_references:
                self.move_files_and_update_dynamo(
                    arf_document_references, arf_bucket_name, arf_table_name
                )

            if lg_document_references:
                self.validate_number_of_documents(lg_table_name, lg_document_references)
                self.move_files_and_update_dynamo(
                    lg_document_references, lg_bucket_name, lg_table_name
                )

        except ClientError as e:
            logger.error(f"Error with one of our services: {e}")

    def move_files_and_update_dynamo(
        self, document_references: list, bucket_name: str, table_name: str
    ):
        self.copy_files_from_staging_bucket(document_references, bucket_name)
        self.delete_files_from_staging_bucket(document_references, bucket_name)
        self.update_dynamo_table(table_name, document_references)

    def copy_files_from_staging_bucket(
        self, document_references: list, bucket_name: str
    ):
        staging_bucket = os.environ["STAGING_STORE_BUCKET_NAME"]

        for document_reference in document_references:
            dest_file_key = f"{self.nhs_number}/{document_reference}"

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

    def validate_number_of_documents(self, table_name: str, document_references: list):
        query_response = self.dynamo_service.simple_query(
            table_name=table_name,
            key_condition_expression=Key("NhsNumber").eq(self.nhs_number),
        )

        if len(query_response["Items"]) != len(document_references):
            raise UploadConfirmResultException(
                f"Number of document references not equal to number of documents in "
                f"dynamo table for nhs number: {self.nhs_number}"
            )
