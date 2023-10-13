import json
import logging
import os

import pydantic
from enums.metadata_field_names import DocumentReferenceMetadataFields
from models.nhs_document_reference import NHSDocumentReference
from models.staging_metadata import MetadataFile, StagingMetadata
from services.dynamo_service import DynamoDBService
from services.lloyd_george_validator import (LGInvalidFilesException,
                                             validate_lg_file_names)
from services.s3_service import S3Service
from services.sqs_service import SQSService
from utils.exceptions import InvalidMessageException
from utils.utilities import create_reference_id

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class BulkUploadService:
    def __init__(
        self,
    ):
        self.s3_service = S3Service()
        self.dynamo_service = DynamoDBService()
        self.sqs_service = SQSService()

        self.staging_bucket_name = os.environ["STAGING_STORE_BUCKET_NAME"]
        self.lg_bucket_name = os.environ["LLOYD_GEORGE_BUCKET_NAME"]
        self.lg_dynamo_table = os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]
        self.invalid_queue_url = os.environ["INVALID_SQS_QUEUE_URL"]

        self.pdf_content_type = "application/pdf"
        self.dynamo_records_in_transaction: list[NHSDocumentReference] = []
        self.dest_bucket_files_in_transaction = []

    def handle_sqs_message(self, message: dict):
        if message["eventSource"] != "aws:sqs":
            logger.warning("Rejecting message as not coming from sqs")
            raise InvalidMessageException("Message not coming from sqs")

        logger.info("Parsing message from sqs...")

        try:
            staging_metadata_json = message["body"]
            staging_metadata = StagingMetadata.model_validate_json(
                staging_metadata_json
            )
        except (pydantic.ValidationError, KeyError) as e:
            logger.error(f"Got unrecognised message: {message}")
            logger.error(e)
            raise InvalidMessageException(str(e))

        try:
            self.validate_files(staging_metadata)
        except LGInvalidFilesException as e:
            logger.info(
                f"Detected invalid file name related to patient number: {staging_metadata.nhs_number}"
            )
            logger.info("Will stop processing Lloyd George record for this patient")
            return self.handle_invalid_message(message, staging_metadata.nhs_number, e)

        logger.info("Validation complete. Start copying Lloyd George records across")

        self.init_transaction()

        try:
            self.create_lg_records_and_copy_files(staging_metadata)
        except Exception as e:
            logger.debug(f"Got unexpected error during file transfer: {str(e)}")
            logger.debug("Will try to rollback any change to database and bucket")
            self.rollback_transaction()

    def validate_files(self, staging_metadata: StagingMetadata):
        file_names = [
            os.path.basename(metadata.file_path) for metadata in staging_metadata.files
        ]
        validate_lg_file_names(file_names)

    def init_transaction(self):
        self.dynamo_records_in_transaction = []
        self.dest_bucket_files_in_transaction = []

    def create_lg_records_and_copy_files(self, staging_metadata: StagingMetadata):
        nhs_number = staging_metadata.nhs_number

        for file_metadata in staging_metadata.files:
            document_reference = self.convert_to_document_reference(
                file_metadata, nhs_number
            )
            source_file_key = self.strip_leading_slash(file_metadata.file_path)
            dest_file_key = document_reference.s3_file_key
            self.create_record_in_lg_dynamo_table(document_reference)
            self.copy_to_lg_bucket(
                source_file_key=source_file_key, dest_file_key=dest_file_key
            )

    def create_record_in_lg_dynamo_table(self, document_reference):
        self.dynamo_service.post_item_service(
            self.lg_dynamo_table, document_reference.to_dict()
        )
        self.dynamo_records_in_transaction.append(document_reference)

    def copy_to_lg_bucket(self, source_file_key: str, dest_file_key: str):
        self.s3_service.copy_across_bucket(
            source_bucket=self.staging_bucket_name,
            source_file_key=source_file_key,
            dest_bucket=self.lg_bucket_name,
            dest_file_key=dest_file_key,
        )
        self.dest_bucket_files_in_transaction.append(dest_file_key)

    def convert_to_document_reference(
        self, file_metadata: MetadataFile, nhs_number: str
    ) -> NHSDocumentReference:
        reference_id = create_reference_id()
        file_name = os.path.basename(file_metadata.file_path)

        return NHSDocumentReference(
            nhs_number=nhs_number,
            content_type=self.pdf_content_type,
            file_name=file_name,
            reference_id=reference_id,
            s3_bucket_name=self.lg_bucket_name,
        )

    def rollback_transaction(self):
        for document_reference in self.dynamo_records_in_transaction:
            primary_key_name = DocumentReferenceMetadataFields.ID.field_name
            primary_key_value = document_reference.id
            deletion_key = {primary_key_name: primary_key_value}
            self.dynamo_service.delete_item(
                table_name=self.lg_dynamo_table, key=deletion_key
            )
        for dest_bucket_file_name in self.dest_bucket_files_in_transaction:
            pass
            # delete the copied file here

    def handle_invalid_message(self, message: dict, nhs_number: str, error=None):
        # Currently we just drop the invalid message to invalid queue.
        # In future ticket, will change this to record the error in dynamo db

        message = {"original_message": message["body"], "nhs_number": nhs_number}
        if error:
            message["error_message"] = str(error)

        self.sqs_service.send_message(
            queue_url=self.invalid_queue_url, message_body=json.dumps(message)
        )
        logger.info(f"Sent message to invalid queue: {message}")

    @staticmethod
    def strip_leading_slash(filepath: str) -> str:
        # Handle the filepaths irregularity in the given example of metadata.csv,
        # where some filepaths begin with '/' and some does not.
        return filepath.lstrip("/")
