import os

from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from utils.audit_logging_setup import LoggingService
from utils.lambda_exceptions import UploadConfirmResultException

logger = LoggingService(__name__)


class UploadConfirmResultService:
    def __init__(self, nhs_number):
        self.dynamo_service = DynamoDBService()
        self.s3_service = S3Service()
        self.nhs_number = nhs_number
        self.staging_bucket = os.environ["STAGING_STORE_BUCKET_NAME"]

    def process_documents(self, documents: dict):
        lg_table_name = os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]
        lg_bucket_name = os.environ["LLOYD_GEORGE_BUCKET_NAME"]
        arf_bucket_name = os.environ["DOCUMENT_STORE_BUCKET_NAME"]
        arf_table_name = os.environ["DOCUMENT_STORE_DYNAMODB_NAME"]
        arf_document_references: list[str] = documents.get("ARF")
        lg_document_references: list[str] = documents.get("LG")

        if not arf_document_references or not lg_document_references:
            logger.error("Document object is missing a document type")
            raise UploadConfirmResultException(
                400, LambdaError.UploadConfirmResultProps
            )

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
            logger.error(f"Error with one of our services: {str(e)}")
            raise UploadConfirmResultException(
                500, LambdaError.UploadConfirmResultAWSFailure
            )

    def move_files_and_update_dynamo(
        self, document_references: list, bucket_name: str, table_name: str
    ):
        self.copy_files_from_staging_bucket(document_references, bucket_name)

        logger.info(
            "Files successfully copied, deleting files from staging bucket and updating dynamo db table"
        )

        for document_reference in document_references:
            self.delete_file_from_staging_bucket(document_reference)
            self.update_dynamo_table(table_name, document_reference, bucket_name)

    def copy_files_from_staging_bucket(
        self, document_references: list, bucket_name: str
    ):
        logger.info("Copying files from staging bucket")

        for document_reference in document_references:
            dest_file_key = f"{self.nhs_number}/{document_reference}"

            self.s3_service.copy_across_bucket(
                source_bucket=self.staging_bucket,
                source_file_key=document_reference,
                dest_bucket=bucket_name,
                dest_file_key=dest_file_key,
            )

    def delete_file_from_staging_bucket(self, document_reference: str):
        self.s3_service.delete_object(self.staging_bucket, document_reference)

    def update_dynamo_table(
        self, table_name: str, document_reference: str, bucket_name: str
    ):
        file_location = f"s3://{bucket_name}/{self.nhs_number}/{document_reference}"

        self.dynamo_service.update_item(
            table_name,
            document_reference,
            {"Uploaded": True, "FileLocation": file_location},
        )

    def validate_number_of_documents(self, table_name: str, document_references: list):
        logger.info(
            "Checking number of document references in list matches number of documents in dynamo table"
        )

        filter_by_nhs_number = Attr("NhsNumber").eq(self.nhs_number)

        query_response = self.dynamo_service.scan_table(
            table_name=table_name, filter_expression=filter_by_nhs_number
        )

        items = query_response.get("Items", None)

        if len(items) != len(document_references):
            raise UploadConfirmResultException(
                400, LambdaError.UploadConfirmResultBadRequest
            )
