import json
import os
import uuid

import pydantic
from botocore.exceptions import ClientError
from enums.patient_ods_inactive_status import PatientOdsInactiveStatus
from enums.upload_status import UploadStatus
from enums.virus_scan_result import VirusScanResult
from models.nhs_document_reference import NHSDocumentReference
from models.staging_metadata import MetadataFile, StagingMetadata
from repositories.bulk_upload.bulk_upload_dynamo_repository import (
    BulkUploadDynamoRepository,
)
from repositories.bulk_upload.bulk_upload_s3_repository import BulkUploadS3Repository
from repositories.bulk_upload.bulk_upload_sqs_repository import BulkUploadSqsRepository
from utils.audit_logging_setup import LoggingService
from utils.exceptions import (
    BulkUploadException,
    DocumentInfectedException,
    InvalidMessageException,
    PatientRecordAlreadyExistException,
    PdsErrorException,
    PdsTooManyRequestsException,
    S3FileNotFoundException,
    VirusScanFailedException,
    VirusScanNoResultException,
)
from utils.lloyd_george_validator import (
    LGInvalidFilesException,
    allowed_to_ingest_ods_code,
    getting_patient_info_from_pds,
    validate_filename_with_patient_details,
    validate_lg_file_names,
)
from utils.request_context import request_context
from utils.unicode_utils import (
    contains_accent_char,
    convert_to_nfc_form,
    convert_to_nfd_form,
)

logger = LoggingService(__name__)


class BulkUploadService:
    def __init__(self):
        self.dynamo_repository = BulkUploadDynamoRepository()
        self.sqs_repository = BulkUploadSqsRepository()
        self.s3_repository = BulkUploadS3Repository()

        self.pdf_content_type = "application/pdf"
        self.unhandled_messages = []
        self.file_path_cache = {}

    def process_message_queue(self, records: list):
        for index, message in enumerate(records, start=1):
            try:
                logger.info(f"Processing message {index} of {len(records)}")
                self.handle_sqs_message(message)
            except (PdsTooManyRequestsException, PdsErrorException) as error:
                logger.error(error)

                logger.info(
                    "Cannot validate patient due to PDS responded with Too Many Requests"
                )
                logger.info("Cannot process for now due to PDS rate limit reached.")
                logger.info(
                    "All remaining messages in this batch will be returned to sqs queue to retry later."
                )

                all_unprocessed_message = records[index - 1 :]
                for unprocessed_message in all_unprocessed_message:
                    self.sqs_repository.put_sqs_message_back_to_queue(
                        unprocessed_message
                    )
                raise BulkUploadException(
                    "Bulk upload process paused due to PDS rate limit reached"
                )
            except (
                ClientError,
                InvalidMessageException,
                LGInvalidFilesException,
                Exception,
            ) as error:
                self.unhandled_messages.append(message)
                logger.info(f"Failed to process current message due to error: {error}")
                logger.info("Continue on next message")

        logger.info(
            f"Finish Processing successfully {len(records) - len(self.unhandled_messages)} of {len(records)} messages"
        )
        if self.unhandled_messages:
            logger.info("Unable to process the following messages:")
            for message in self.unhandled_messages:
                message_body = json.loads(message.get("body", "{}"))
                request_context.patient_nhs_no = message_body.get(
                    "NHS-NO", "no number found"
                )
                logger.info(message_body)

    def handle_sqs_message(self, message: dict):
        logger.info("Validating SQS event")
        patient_ods_code = ""
        accepted_reason = None
        try:
            staging_metadata_json = message["body"]
            staging_metadata = StagingMetadata.model_validate_json(
                staging_metadata_json
            )
        except (pydantic.ValidationError, KeyError) as e:
            logger.error(f"Got incomprehensible message: {message}")
            logger.error(e)
            raise InvalidMessageException(str(e))

        logger.info("SQS event is valid. Validating NHS number and file names")
        try:
            file_names = [
                os.path.basename(metadata.file_path)
                for metadata in staging_metadata.files
            ]
            request_context.patient_nhs_no = staging_metadata.nhs_number
            validate_lg_file_names(file_names, staging_metadata.nhs_number)

            pds_patient_details = getting_patient_info_from_pds(
                staging_metadata.nhs_number
            )
            patient_ods_code = (
                pds_patient_details.get_ods_code_or_inactive_status_for_gp()
            )
            is_name_validation_based_on_historic_name = (
                validate_filename_with_patient_details(file_names, pds_patient_details)
            )
            if is_name_validation_based_on_historic_name:
                accepted_reason = self.concatenate_acceptance_reason(
                    accepted_reason, "Patient matched on historical name"
                )
            if not allowed_to_ingest_ods_code(patient_ods_code):
                raise LGInvalidFilesException("Patient not registered at your practice")
            patient_death_notification_status = (
                pds_patient_details.get_death_notification_status()
            )
            if patient_death_notification_status:
                deceased_accepted_reason = (
                    f"Patient is deceased - {patient_death_notification_status.name}"
                )
                accepted_reason = self.concatenate_acceptance_reason(
                    accepted_reason, deceased_accepted_reason
                )
            if patient_ods_code is PatientOdsInactiveStatus.RESTRICTED:
                accepted_reason = self.concatenate_acceptance_reason(
                    accepted_reason, "PDS record is restricted"
                )

        except (
            LGInvalidFilesException,
            PatientRecordAlreadyExistException,
        ) as error:
            logger.info(
                f"Detected issue related to patient number: {staging_metadata.nhs_number}"
            )
            logger.error(error)
            logger.info("Will stop processing Lloyd George record for this patient.")

            reason = str(error)
            self.dynamo_repository.write_report_upload_to_dynamo(
                staging_metadata, UploadStatus.FAILED, reason, patient_ods_code
            )
            return

        logger.info(
            "NHS Number and filename validation complete. Checking virus scan has marked files as Clean"
        )

        try:
            self.resolve_source_file_path(staging_metadata)
            self.s3_repository.check_virus_result(
                staging_metadata, self.file_path_cache
            )
        except VirusScanNoResultException as e:
            logger.info(e)
            logger.info(
                f"Waiting on virus scan results for: {staging_metadata.nhs_number}, adding message back to queue"
            )
            if staging_metadata.retries > 14:
                err = (
                    "File was not scanned for viruses before maximum retries attempted"
                )
                self.dynamo_repository.write_report_upload_to_dynamo(
                    staging_metadata, UploadStatus.FAILED, err, patient_ods_code
                )
            else:
                self.sqs_repository.put_staging_metadata_back_to_queue(staging_metadata)
            return
        except (VirusScanFailedException, DocumentInfectedException) as e:
            logger.info(e)
            logger.info(
                f"Virus scan results check failed for: {staging_metadata.nhs_number}, removing from queue"
            )
            logger.info("Will stop processing Lloyd George record for this patient")

            self.dynamo_repository.write_report_upload_to_dynamo(
                staging_metadata,
                UploadStatus.FAILED,
                "One or more of the files failed virus scanner check",
                patient_ods_code,
            )
            return
        except S3FileNotFoundException as e:
            logger.info(e)
            logger.info(
                f"One or more of the files is not accessible from S3 bucket for patient {staging_metadata.nhs_number}"
            )
            logger.info("Will stop processing Lloyd George record for this patient")

            self.dynamo_repository.write_report_upload_to_dynamo(
                staging_metadata,
                UploadStatus.FAILED,
                "One or more of the files is not accessible from staging bucket",
                patient_ods_code,
            )
            return

        logger.info("Virus result validation complete. Initialising transaction")

        self.s3_repository.init_transaction()
        self.dynamo_repository.init_transaction()

        logger.info(
            "Transaction initialised. Transferring files to main S3 bucket and creating metadata"
        )

        try:
            self.create_lg_records_and_copy_files(staging_metadata, patient_ods_code)
            logger.info(
                f"Successfully uploaded the Lloyd George records for patient: {staging_metadata.nhs_number}",
                {"Result": "Successful upload"},
            )
        except ClientError as e:
            logger.info(
                f"Got unexpected error during file transfer: {str(e)}",
                {"Result": "Unsuccessful upload"},
            )
            logger.info("Will try to rollback any change to database and bucket")
            self.rollback_transaction()

            self.dynamo_repository.write_report_upload_to_dynamo(
                staging_metadata,
                UploadStatus.FAILED,
                "Validation passed but error occurred during file transfer",
                patient_ods_code,
            )
            return

        logger.info(
            "File transfer complete. Removing uploaded files from staging bucket"
        )
        self.s3_repository.remove_ingested_file_from_source_bucket()

        logger.info(
            f"Completed file ingestion for patient {staging_metadata.nhs_number}",
            {"Result": "Successful upload"},
        )
        logger.info("Reporting transaction successful")
        self.dynamo_repository.write_report_upload_to_dynamo(
            staging_metadata,
            UploadStatus.COMPLETE,
            accepted_reason,
            patient_ods_code,
        )

    def resolve_source_file_path(self, staging_metadata: StagingMetadata):
        sample_file_path = staging_metadata.files[0].file_path

        if not contains_accent_char(sample_file_path):
            logger.info("No accented character detected in file path.")
            self.file_path_cache = {
                file.file_path: self.strip_leading_slash(file.file_path)
                for file in staging_metadata.files
            }
            return

        logger.info("Detected accented character in file path.")
        logger.info("Will take special steps to handle file names.")

        resolved_file_paths = {}
        for file in staging_metadata.files:
            file_path_in_metadata = file.file_path
            file_path_without_leading_slash = self.strip_leading_slash(
                file_path_in_metadata
            )
            file_path_in_nfc_form = convert_to_nfc_form(file_path_without_leading_slash)
            file_path_in_nfd_form = convert_to_nfd_form(file_path_without_leading_slash)

            if self.s3_repository.file_exists_on_staging_bucket(file_path_in_nfc_form):
                resolved_file_paths[file_path_in_metadata] = file_path_in_nfc_form
            elif self.s3_repository.file_exists_on_staging_bucket(
                file_path_in_nfd_form
            ):
                resolved_file_paths[file_path_in_metadata] = file_path_in_nfd_form
            else:
                logger.info(
                    "No file matching the provided file path was found on S3 bucket"
                )
                logger.info("Please check whether files are named correctly")
                raise S3FileNotFoundException(
                    f"Failed to access file {sample_file_path}"
                )

        self.file_path_cache = resolved_file_paths

    def create_lg_records_and_copy_files(
        self, staging_metadata: StagingMetadata, current_gp_ods: str
    ):
        nhs_number = staging_metadata.nhs_number

        for file_metadata in staging_metadata.files:
            document_reference = self.convert_to_document_reference(
                file_metadata, nhs_number, current_gp_ods
            )

            source_file_key = self.file_path_cache[file_metadata.file_path]
            dest_file_key = document_reference.s3_file_key

            self.s3_repository.copy_to_lg_bucket(
                source_file_key=source_file_key, dest_file_key=dest_file_key
            )
            document_reference.set_uploaded_to_true()
            self.dynamo_repository.create_record_in_lg_dynamo_table(document_reference)

    def rollback_transaction(self):
        try:
            self.s3_repository.rollback_transaction()
            self.dynamo_repository.rollback_transaction()
            logger.info("Rolled back an incomplete transaction")
        except ClientError as e:
            logger.error(
                f"Failed to rollback the incomplete transaction due to error: {e}"
            )

    def convert_to_document_reference(
        self, file_metadata: MetadataFile, nhs_number: str, current_gp_ods: str
    ) -> NHSDocumentReference:
        s3_bucket_name = self.s3_repository.lg_bucket_name
        file_name = os.path.basename(file_metadata.file_path)

        document_reference = NHSDocumentReference(
            reference_id=str(uuid.uuid4()),
            nhs_number=nhs_number,
            file_name=file_name,
            s3_bucket_name=s3_bucket_name,
            current_gp_ods=current_gp_ods,
        )
        document_reference.set_virus_scanner_result(VirusScanResult.CLEAN)

        return document_reference

    @staticmethod
    def strip_leading_slash(filepath: str) -> str:
        # Handle the filepaths irregularity in the given example of metadata.csv,
        # where some filepaths begin with '/' and some does not.
        return filepath.lstrip("/")

    @staticmethod
    def concatenate_acceptance_reason(previous_reasons: str | None, new_reason: str):
        return previous_reasons + ", " + new_reason if previous_reasons else new_reason
