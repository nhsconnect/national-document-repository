import logging
import os

import pydantic
from botocore.exceptions import ClientError
from enums.metadata_field_names import DocumentReferenceMetadataFields
from enums.virus_scan_result import SCAN_RESULT_TAG_KEY, VirusScanResult
from models.bulk_upload_status import FailedUpload, SuccessfulUpload
from models.nhs_document_reference import NHSDocumentReference
from models.staging_metadata import MetadataFile, StagingMetadata
from services.dynamo_service import DynamoDBService
from services.s3_service import S3Service
from services.sqs_service import SQSService
from utils.exceptions import (
    InvalidMessageException,
    TagNotFoundException,
    DocumentInfectedException,
    VirusScanFailedException,
    VirusScanNoResultException,
    S3FileNotFoundException,
)
from utils.lloyd_george_validator import LGInvalidFilesException, validate_lg_file_names
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
        self.bulk_upload_report_dynamo_table = os.environ["BULK_UPLOAD_DYNAMODB_NAME"]
        self.invalid_queue_url = os.environ["INVALID_SQS_QUEUE_URL"]
        self.metadata_queue_url = os.environ["METADATA_SQS_QUEUE_URL"]
        self.pdf_content_type = "application/pdf"
        self.dynamo_records_in_transaction: list[NHSDocumentReference] = []
        self.dest_bucket_files_in_transaction = []

    def handle_sqs_message(self, message: dict):
        try:
            logger.info("Parsing message from sqs...")
            staging_metadata_json = message["body"]
            staging_metadata = StagingMetadata.model_validate_json(
                staging_metadata_json
            )
        except (pydantic.ValidationError, KeyError) as e:
            logger.error(f"Got incomprehensible message: {message}")
            logger.error(e)
            raise InvalidMessageException(str(e))

        try:
            logger.info("Running validation for file names...")
            self.validate_files(staging_metadata)
        except LGInvalidFilesException as error:
            logger.info(
                f"Detected invalid file name related to patient number: {staging_metadata.nhs_number}"
            )
            logger.info("Will stop processing Lloyd George record for this patient")

            failure_reason = str(error)
            self.report_upload_failure(staging_metadata, failure_reason)
            return

        logger.info("File validation complete. Checking virus scan results")

        try:
            logger.info("Running validation for virus scan results...")
            self.check_virus_result(staging_metadata)
        except VirusScanNoResultException as e:
            logger.info(e)
            logger.info(
                f"Waiting on virus scan results for: {staging_metadata.nhs_number}, adding message back to queue"
            )
            self.put_message_back_to_queue(staging_metadata)
            return
        except (VirusScanFailedException, DocumentInfectedException) as e:
            logger.info(e)
            logger.info(
                f"Virus scan results check failed for: {staging_metadata.nhs_number}, removing from queue"
            )
            logger.info("Will stop processing Lloyd George record for this patient")

            self.report_upload_failure(
                staging_metadata, "One or more of the files failed virus scanner check"
            )
            return
        except S3FileNotFoundException as e:
            logger.info(e)
            logger.info(
                f"One or more of the files is not accessible from S3 bucket for patient {staging_metadata.nhs_number}"
            )
            logger.info("Will stop processing Lloyd George record for this patient")

            self.report_upload_failure(
                staging_metadata,
                "One or more of the files is not accessible from staging bucket",
            )
            return

        logger.info(
            "Virus result validation complete. Start uploading Lloyd George records"
        )

        self.init_transaction()

        try:
            self.create_lg_records_and_copy_files(staging_metadata)
            logger.info(
                f"Successfully uploaded the Lloyd George records for patient: {staging_metadata.nhs_number}"
            )
        except Exception as e:
            logger.info(f"Got unexpected error during file transfer: {str(e)}")
            logger.info("Will try to rollback any change to database and bucket")
            self.rollback_transaction()

            self.report_upload_failure(
                staging_metadata,
                "Validation passed but error occurred during file transfer",
            )
            return

        self.report_upload_complete(staging_metadata)

    def validate_files(self, staging_metadata: StagingMetadata):
        # Delegate to lloyd_george_validator service
        # Expect LGInvalidFilesException to be raised when validation fails
        file_names = [
            os.path.basename(metadata.file_path) for metadata in staging_metadata.files
        ]

        validate_lg_file_names(file_names, staging_metadata.nhs_number)

    def check_virus_result(self, staging_metadata: StagingMetadata):
        for file_metadata in staging_metadata.files:
            source_file_key = self.strip_leading_slash(file_metadata.file_path)
            file_path = file_metadata.file_path
            try:
                scan_result = self.s3_service.get_tag_value(
                    self.staging_bucket_name, source_file_key, SCAN_RESULT_TAG_KEY
                )
                if scan_result == VirusScanResult.CLEAN:
                    continue
                elif scan_result == VirusScanResult.INFECTED:
                    raise DocumentInfectedException(
                        f"Found infected document filepath: {file_path}"
                    )
                else:
                    # handle cases other than Clean or Infected e.g. Unscannable, Error
                    raise VirusScanFailedException(
                        f"Failed to scan document filepath: {file_path}, scan result was {scan_result}"
                    )
            except TagNotFoundException:
                raise VirusScanNoResultException(
                    f"Virus scan result not found for document: {file_path}"
                )
            except ClientError as e:
                if "AccessDenied" in str(e) or "NoSuchKey" in str(e):
                    logger.info(
                        f"Failed to check object tag for given file_path: {file_path}"
                    )
                    logger.info(
                        "file_path may be incorrect or contain invalid character"
                    )
                    raise S3FileNotFoundException(f"Failed to access file {file_path}")
                else:
                    raise e

        logger.info(
            f"Verified that all documents for patient {staging_metadata.nhs_number} are clean."
        )

    def put_message_back_to_queue(self, staging_metadata: StagingMetadata):
        self.sqs_service.send_message_with_nhs_number_attr(
            queue_url=self.metadata_queue_url,
            message_body=staging_metadata.model_dump_json(by_alias=True),
            nhs_number=staging_metadata.nhs_number,
            delay_seconds=60 * 5,
        )

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

    def create_record_in_lg_dynamo_table(
        self, document_reference: NHSDocumentReference
    ):
        self.dynamo_service.create_item(
            table_name=self.lg_dynamo_table, item=document_reference.to_dict()
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
        try:
            for document_reference in self.dynamo_records_in_transaction:
                primary_key_name = DocumentReferenceMetadataFields.ID.value
                primary_key_value = document_reference.id
                deletion_key = {primary_key_name: primary_key_value}
                self.dynamo_service.delete_item(
                    table_name=self.lg_dynamo_table, key=deletion_key
                )
            for dest_bucket_file_key in self.dest_bucket_files_in_transaction:
                self.s3_service.delete_object(
                    s3_bucket_name=self.lg_bucket_name, file_key=dest_bucket_file_key
                )
            logger.info("Rolled back an incomplete transaction")
        except ClientError as e:
            logger.error(
                f"Failed to rollback the incomplete transaction due to error: {e}"
            )

    def report_upload_complete(self, staging_metadata: StagingMetadata):
        nhs_number = staging_metadata.nhs_number
        for file in staging_metadata.files:
            dynamo_record = SuccessfulUpload(
                nhs_number=nhs_number,
                file_path=file.file_path,
            )
            self.dynamo_service.create_item(
                table_name=self.bulk_upload_report_dynamo_table,
                item=dynamo_record.model_dump(by_alias=True),
            )

    def report_upload_failure(
        self, staging_metadata: StagingMetadata, failure_reason: str
    ):
        nhs_number = staging_metadata.nhs_number

        for file in staging_metadata.files:
            dynamo_record = FailedUpload(
                nhs_number=nhs_number,
                failure_reason=failure_reason,
                file_path=file.file_path,
            )
            self.dynamo_service.create_item(
                table_name=self.bulk_upload_report_dynamo_table,
                item=dynamo_record.model_dump(by_alias=True),
            )

    @staticmethod
    def strip_leading_slash(filepath: str) -> str:
        # Handle the filepaths irregularity in the given example of metadata.csv,
        # where some filepaths begin with '/' and some does not.
        return filepath.lstrip("/")
