import csv
import os
import shutil
import tempfile
import uuid
from datetime import datetime
from typing import Iterable

import pydantic
import regex
from botocore.exceptions import ClientError
from enums.upload_status import UploadStatus
from models.staging_metadata import (
    METADATA_FILENAME,
    NHS_NUMBER_FIELD_NAME,
    ODS_CODE,
    MetadataFile,
    StagingMetadata,
)
from repositories.bulk_upload.bulk_upload_dynamo_repository import (
    BulkUploadDynamoRepository,
)
from services.base.s3_service import S3Service
from services.base.sqs_service import SQSService
from utils.audit_logging_setup import LoggingService
from utils.exceptions import BulkUploadMetadataException, InvalidFileNameException

logger = LoggingService(__name__)
unsuccessful = "Unsuccessful bulk upload"


class V2BulkUploadMetadataService:
    def __init__(self, practice_directory: str):
        self.s3_service = S3Service()
        self.sqs_service = SQSService()
        self.dynamo_repository = BulkUploadDynamoRepository()

        self.staging_bucket_name = os.environ["STAGING_STORE_BUCKET_NAME"]
        self.metadata_queue_url = os.environ["METADATA_SQS_QUEUE_URL"]

        self.temp_download_dir = tempfile.mkdtemp()

        self.corrections = {}
        self.practice_directory = practice_directory

    def process_metadata(self):
        try:
            metadata_file = self.download_metadata_from_s3()
            staging_metadata_list = self.csv_to_staging_metadata(metadata_file)
            logger.info("Finished parsing metadata")

            self.send_metadata_to_fifo_sqs(staging_metadata_list)
            logger.info("Sent bulk upload metadata to sqs queue")

            self.copy_metadata_to_dated_folder()

            self.clear_temp_storage()

        except pydantic.ValidationError as e:
            failure_msg = f"Failed to parse {METADATA_FILENAME}: {str(e)}"
            logger.error(failure_msg, {"Result": unsuccessful})
            raise BulkUploadMetadataException(failure_msg)
        except KeyError as e:
            failure_msg = f"Failed due to missing key: {str(e)}"
            logger.error(failure_msg, {"Result": unsuccessful})
            raise BulkUploadMetadataException(failure_msg)
        except ClientError as e:
            if "HeadObject" in str(e):
                failure_msg = f'No metadata file could be found with the name "{METADATA_FILENAME}"'
            else:
                failure_msg = str(e)
            logger.error(failure_msg, {"Result": unsuccessful})
            raise BulkUploadMetadataException(failure_msg)

    def download_metadata_from_s3(self) -> str:
        logger.info(f"Fetching {METADATA_FILENAME} from bucket")

        local_file_path = os.path.join(self.temp_download_dir, METADATA_FILENAME)
        self.s3_service.download_file(
            s3_bucket_name=self.staging_bucket_name,
            file_key=f"{self.practice_directory}/{METADATA_FILENAME}",
            download_path=local_file_path,
        )
        return local_file_path

    def csv_to_staging_metadata(self, csv_file_path: str) -> list[StagingMetadata]:
        logger.info("Parsing bulk upload metadata")
        patients = {}
        with open(
            csv_file_path, mode="r", encoding="utf-8-sig", errors="replace"
        ) as csv_file_handler:
            csv_reader: Iterable[dict] = csv.DictReader(csv_file_handler)
            for row in csv_reader:
                nhs_number = row.get(NHS_NUMBER_FIELD_NAME)
                ods_code = row.get(ODS_CODE)
                file_metadata = MetadataFile.model_validate(row)
                key = (nhs_number, ods_code)
                if key not in patients:
                    patients[key] = [file_metadata]
                else:
                    patients[key].append(file_metadata)
                try:
                    valid_filename = self.validate_record_filename(row["FILEPATH"])
                    if valid_filename != "":
                        self.corrections.update({row["FILEPATH"]: valid_filename})
                except InvalidFileNameException as error:
                    logger.error(
                        f"Failed to process {row['FILEPATH']} due to error: {error}"
                    )
                    failed_entry = StagingMetadata(
                        nhs_number=nhs_number, files=patients[nhs_number, ods_code]
                    )
                    self.dynamo_repository.write_report_upload_to_dynamo(
                        failed_entry, UploadStatus.FAILED, str(error)
                    )
        return [
            StagingMetadata(
                nhs_number=nhs_number,
                files=patients[nhs_number, ods_code],
            )
            for (nhs_number, ods_code) in patients
        ]

    def send_metadata_to_fifo_sqs(
        self, staging_metadata_list: list[StagingMetadata]
    ) -> None:
        sqs_group_id = f"bulk_upload_{uuid.uuid4()}"

        for staging_metadata in staging_metadata_list:
            nhs_number = staging_metadata.nhs_number
            logger.info(f"Sending metadata for patientId: {nhs_number}")

            self.sqs_service.send_message_with_nhs_number_attr_fifo(
                queue_url=self.metadata_queue_url,
                message_body=staging_metadata.model_dump_json(by_alias=True),
                nhs_number=nhs_number,
                group_id=sqs_group_id,
            )

    def copy_metadata_to_dated_folder(self):
        logger.info("Copying metadata CSV to dated folder")

        current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M")

        self.s3_service.copy_across_bucket(
            self.staging_bucket_name,
            f"{self.practice_directory}/{METADATA_FILENAME}",
            self.staging_bucket_name,
            f"metadata/{current_datetime}.csv",
        )

        self.s3_service.delete_object(self.staging_bucket_name, METADATA_FILENAME)

    def clear_temp_storage(self):
        logger.info("Clearing temp storage directory")
        shutil.rmtree(self.temp_download_dir)

    def validate_record_filename(self, file_name) -> str:
        logger.info(f"Processing file name {file_name}")

        file_path_prefix, current_file_name = self.extract_document_path(file_name)

        first_document_number, second_document_number, current_file_name = (
            self.extract_document_number_bulk_upload_file_name(current_file_name)
        )

        lloyd_george_record, current_file_name = (
            self.extract_lloyd_george_record_from_bulk_upload_file_name(
                current_file_name
            )
        )
        patient_name, current_file_name = (
            self.extract_patient_name_from_bulk_upload_file_name(current_file_name)
        )

        if sum(c.isdigit() for c in current_file_name) != 18:
            logger.info("Failed to find NHS number or date")
            raise InvalidFileNameException("Incorrect NHS number or date format")

        nhs_number, current_file_name = (
            self.extract_nhs_number_from_bulk_upload_file_name(current_file_name)
        )
        day, month, year, current_file_name = (
            self.extract_date_from_bulk_upload_file_name(current_file_name)
        )
        file_extension = self.extract_file_extension_from_bulk_upload_file_name(
            current_file_name
        )
        file_name_correction = self.assemble_valid_file_name(
            file_path_prefix,
            first_document_number,
            second_document_number,
            lloyd_george_record,
            patient_name,
            nhs_number,
            day,
            month,
            year,
            file_extension,
        )
        if file_name_correction:
            logger.info(f"Finished processing, new file name is: {file_name}")
            return file_name_correction
        else:
            return ""

    @staticmethod
    def extract_document_path(
        file_path: str,
    ) -> tuple[str, str]:
        document_number_expression = r"(.*[/])*((\d+)[^0-9]*of[^0-9]*(\d+)(.*))"

        expression_result = regex.search(rf"{document_number_expression}", file_path)

        if expression_result is None:
            logger.info("Failed to find the document path in file name")
            raise InvalidFileNameException("Incorrect document path format")

        current_file_path = expression_result.group(2)
        if expression_result.group(1) is None:
            file_path = file_path.replace(current_file_path, "")
            file_path = file_path[: file_path.rfind("/") + 1]
        else:
            file_path = expression_result.group(1)
        return file_path, current_file_path

    @staticmethod
    def extract_document_number_bulk_upload_file_name(
        file_path: str,
    ) -> tuple[int, int, str]:
        document_number_expression = r"[^0-9]*(\d+)[^0-9]*of[^0-9]*(\d+)(.*)"
        expression_result = regex.search(rf"{document_number_expression}", file_path)

        if expression_result is None:
            logger.info("Failed to find the document number in file name")
            raise InvalidFileNameException("Incorrect document number format")

        first_document_number = int(expression_result.group(1))
        second_document_number = int(expression_result.group(2))
        current_file_path = expression_result.group(3)

        return first_document_number, second_document_number, current_file_path

    @staticmethod
    def extract_lloyd_george_record_from_bulk_upload_file_name(
        file_path: str,
    ) -> tuple[str, str]:
        _expression = r".*?ll[oO0οՕ〇]yd.*?ge[oO0οՕ〇]rge.*?rec[oO0οՕ〇]rd(.*)"
        lloyd_george_record = regex.search(
            rf"{_expression}", file_path, regex.IGNORECASE
        )
        if lloyd_george_record is None:
            logger.info("Failed to extract Lloyd George Record from file name")
            raise InvalidFileNameException("Invalid Lloyd_George_Record separator")

        current_file_path = lloyd_george_record.group(1)

        lloyd_george_record_text = "Lloyd_George_Record"

        return lloyd_george_record_text, current_file_path

    @staticmethod
    def extract_patient_name_from_bulk_upload_file_name(
        file_path: str,
    ) -> tuple[str, str]:
        document_number_expression = r".*?([\p{L}][^\d]*[\p{L}])(.*)"
        expression_result = regex.search(
            rf"{document_number_expression}", file_path, regex.IGNORECASE
        )

        if expression_result is None:
            logger.info("Failed to find the patient name in the file name")
            raise InvalidFileNameException("Invalid patient name")

        patient_name = expression_result.group(1)
        current_file_path = expression_result.group(2)

        return patient_name, current_file_path

    @staticmethod
    def extract_nhs_number_from_bulk_upload_file_name(
        file_path: str,
    ) -> tuple[str, str]:
        nhs_number_expression = r"((?:[^_]*?\d){10})(.*)"
        expression_result = regex.search(rf"{nhs_number_expression}", file_path)

        if expression_result is None:
            logger.info("Failed to find NHS number in file name")
            raise InvalidFileNameException("Invalid NHS number")

        nhs_number = "".join(regex.findall(r"\d", expression_result.group(1)))
        current_file_path = expression_result.group(2)

        return nhs_number, current_file_path

    @staticmethod
    def extract_date_from_bulk_upload_file_name(file_path):
        date_number_expression = r"(\D+\d{2})(\D*\d{2})(\D*(\d{4}))(.*)"
        expression_result = regex.search(rf"{date_number_expression}", file_path)

        if expression_result is None:
            logger.info("Failed to find date in file name")
            raise InvalidFileNameException("Invalid date format")

        day = "".join(regex.findall(r"\d", expression_result.group(1))).zfill(2)
        month = "".join(regex.findall(r"\d", expression_result.group(2))).zfill(2)
        year = "".join(regex.findall(r"\d", expression_result.group(3)))
        current_file_path = expression_result.group(5)

        try:
            datetime(day=int(day), month=int(month), year=int(year))
        except ValueError as e:
            logger.info(f"Failed to parse date from filename: {e}")
            raise InvalidFileNameException("Invalid date format")

        return day, month, year, current_file_path

    @staticmethod
    def extract_file_extension_from_bulk_upload_file_name(
        file_path: str,
    ) -> str:
        file_extension_expression = r"(\.([^.]*))$"
        expression_result = regex.search(rf"{file_extension_expression}", file_path)

        if expression_result is None:
            logger.info("Failed to find a file extension")
            raise InvalidFileNameException("Invalid file extension")

        file_extension = expression_result.group(1)

        return file_extension

    @staticmethod
    def assemble_valid_file_name(
        file_path_prefix: str,
        first_document_number: int,
        second_document_number: int,
        lloyd_george_record: str,
        patient_name: str,
        nhs_number: str,
        day: str,
        month: str,
        year: str,
        file_extension: str,
    ) -> str:
        return (
            f"{file_path_prefix}"
            f"{first_document_number}of{second_document_number}"
            f"_{lloyd_george_record}_"
            f"[{patient_name}]_"
            f"[{nhs_number}]_"
            f"[{day}-{month}-{year}]"
            f"{file_extension}"
        )
