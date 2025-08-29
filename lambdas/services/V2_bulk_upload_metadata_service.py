import csv
import os
import shutil
import tempfile
import uuid
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Iterable

import pydantic
import regex
from botocore.exceptions import ClientError
from models.staging_metadata import (
    METADATA_FILENAME,
    NHS_NUMBER_FIELD_NAME,
    ODS_CODE,
    MetadataFile,
    StagingMetadata,
)
from services.base.s3_service import S3Service
from services.base.sqs_service import SQSService
from utils.audit_logging_setup import LoggingService
from utils.exceptions import (
    BulkUploadMetadataException,
    InvalidFileNameException,
    MetadataPreprocessingException,
)
from utils.file_utils import convert_csv_dictionary_to_bytes

logger = LoggingService(__name__)
unsuccessful = "Unsuccessful bulk upload"


class V2BulkUploadMetadataService:
    def __init__(self, practice_directory: str):
        self.s3_service = S3Service()
        self.sqs_service = SQSService()
        self.staging_bucket_name = os.environ["STAGING_STORE_BUCKET_NAME"]
        self.metadata_queue_url = os.environ["METADATA_SQS_QUEUE_URL"]
        self.temp_download_dir = tempfile.mkdtemp()
        self.practice_directory = practice_directory
        self.processed_folder_name = "processed"
        self.processed_date = datetime.now().strftime("%Y-%m-%d %H:%M")

    def process_metadata(self):
        # Pre-processor Lambda
        # 1. Get metadata rows from original metadata.csv
        # 2. Rename rows if required??
        # 3. 
        file_key = f"{self.practice_directory}/{METADATA_FILENAME}"

        metadata_rows = self.get_metadata_rows_from_file(
            file_key=file_key, bucket_name=self.staging_bucket_name
        )

        logger.info("Generating renaming map from metadata")
        renaming_map, rejected_rows, rejected_reasons = self.generate_renaming_map(
            metadata_rows
        )

        logger.info("Processing metadata filenames")
        updated_metadata_rows = self.standardize_filenames(
            renaming_map, rejected_rows, rejected_reasons
        )

        successfully_moved_file = self.move_original_metadata_file(file_key)
        if successfully_moved_file:
            self.s3_service.delete_object(
                s3_bucket_name=self.staging_bucket_name, file_key=file_key
            )

        self.generate_and_save_csv_file(
            csv_dict=updated_metadata_rows, file_key=file_key
        )

        if rejected_reasons:
            file_key = f"{self.practice_directory}/{self.processed_folder_name}/{self.processed_date}/rejections.csv"
            self.generate_and_save_csv_file(
                csv_dict=rejected_reasons, file_key=file_key
            )

        # Metadata Lambda
        try:
            metadata_file = self.download_metadata_from_s3()

            staging_metadata_list = self.csv_to_staging_metadata(metadata_file)
            logger.info("Finished parsing metadata")

            self.send_metadata_to_fifo_sqs(staging_metadata_list)
            logger.info("Sent bulk upload metadata to sqs queue")

            self.copy_metadata_to_dated_folder(METADATA_FILENAME)

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
            file_key=METADATA_FILENAME,
            download_path=local_file_path,
        )
        return local_file_path

    @staticmethod
    def csv_to_staging_metadata(csv_file_path: str) -> list[StagingMetadata]:
        logger.info("Parsing bulk upload metadata")

        patients = {}
        with open(
            csv_file_path, mode="r", encoding="utf-8-sig", errors="replace"
        ) as csv_file_handler:
            csv_reader: Iterable[dict] = csv.DictReader(csv_file_handler)
            for row in csv_reader:
                file_metadata = MetadataFile.model_validate(row)
                nhs_number = row[NHS_NUMBER_FIELD_NAME]
                ods_code = row[ODS_CODE]
                key = (nhs_number, ods_code)
                if key not in patients:
                    patients[key] = [file_metadata]
                else:
                    patients[key].append(file_metadata)

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

    def copy_metadata_to_dated_folder(self, metadata_filename: str):
        logger.info("Copying metadata CSV to dated folder")

        current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M")

        self.s3_service.copy_across_bucket(
            self.staging_bucket_name,
            metadata_filename,
            self.staging_bucket_name,
            f"metadata/{current_datetime}.csv",
        )

        self.s3_service.delete_object(self.staging_bucket_name, metadata_filename)

    def clear_temp_storage(self):
        logger.info("Clearing temp storage directory")
        shutil.rmtree(self.temp_download_dir)

    def preprocessor_lambda_function(self):
        file_key = f"{self.practice_directory}/{METADATA_FILENAME}"

        metadata_rows = self.get_metadata_rows_from_file(
            file_key=file_key, bucket_name=self.staging_bucket_name
        )

        logger.info("Generating renaming map from metadata")
        renaming_map, rejected_rows, rejected_reasons = self.generate_renaming_map(
            metadata_rows
        )

        logger.info("Processing metadata filenames")
        updated_metadata_rows = self.standardize_filenames(
            renaming_map, rejected_rows, rejected_reasons
        )

        successfully_moved_file = self.move_original_metadata_file(file_key)
        if successfully_moved_file:
            self.s3_service.delete_object(
                s3_bucket_name=self.staging_bucket_name, file_key=file_key
            )

        self.generate_and_save_csv_file(
            csv_dict=updated_metadata_rows, file_key=file_key
        )

        if rejected_reasons:
            file_key = f"{self.practice_directory}/{self.processed_folder_name}/{self.processed_date}/rejections.csv"
            self.generate_and_save_csv_file(
                csv_dict=rejected_reasons, file_key=file_key
            )

    def get_metadata_rows_from_file(self, file_key: str, bucket_name: str):
        logger.info(f"Retrieving {file_key}")
        file_exists = self.s3_service.file_exist_on_s3(
            s3_bucket_name=bucket_name, file_key=file_key
        )
        if not file_exists:
            logger.info(f"File {file_key} doesn't exist")
            raise MetadataPreprocessingException("Failed to retrieve metadata")

        response = self.s3_service.client.get_object(Bucket=bucket_name, Key=file_key)

        logger.info(f"Reading {file_key}")
        data = csv.DictReader(response["Body"].read().decode("utf-8-sig").splitlines())
        metadata_rows = [
            row for row in data if any(field.strip() for field in row.values())
        ]
        return metadata_rows

    def generate_renaming_map(self, metadata_rows: list[dict]):
        duplicate_counts = defaultdict(int)
        renaming_map = []
        rejected_rows = []
        rejected_reasons = []

        for original_row in metadata_rows:
            renamed_row = original_row.copy()
            renamed_row = self.update_date_in_row(renamed_row)
            original_filename = original_row.get("FILEPATH")

            try:
                if not original_filename:
                    raise InvalidFileNameException("Filepath is missing")

                validated_filename = self.validate_record_filename(original_filename)
                stripped_file_path = validated_filename.lstrip("/")
                renamed_row["FILEPATH"] = (
                    f"{self.practice_directory}/{stripped_file_path}"
                )
                count = duplicate_counts[validated_filename]

                if count == 0:
                    renaming_map.append((original_row, renamed_row))
                else:
                    rejected_rows.append(original_row)
                    rejected_reasons.append(
                        {
                            "FILEPATH": original_filename,
                            "REASON": "Duplicate filename after renaming",
                        }
                    )

                duplicate_counts[validated_filename] += 1
            except InvalidFileNameException as error:
                rejected_rows.append(original_row)
                rejected_filepath = original_filename if original_filename else "N/A"
                rejected_reasons.append(
                    {"FILEPATH": rejected_filepath, "REASON": str(error)}
                )

        return renaming_map, rejected_rows, rejected_reasons

    def standardize_filenames(
        self,
        renaming_map: list[tuple[dict, dict]],
        rejected_rows: list[dict],
        rejected_reasons: list[dict],
        max_workers=20,
    ):
        logger.info("Standardizing filenames")

        updated_rows = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self.update_record_filename, original_row, updated_row)
                for original_row, updated_row in renaming_map
            ]

            for future in as_completed(futures):
                updated_row, rejected_row, rejected_reason = future.result()
                if updated_row:
                    updated_rows.append(updated_row)
                if rejected_row:
                    rejected_rows.append(rejected_row)
                if rejected_reason:
                    rejected_reasons.append(rejected_reason)

        logger.info("Finished updating and standardizing filenames")
        return updated_rows

    def move_original_metadata_file(self, file_key: str):
        destination_key = f"{self.practice_directory}/{self.processed_folder_name}/{self.processed_date}/{METADATA_FILENAME}"
        logger.info(
            f"Moving original metadata file from {file_key} to {destination_key}"
        )
        try:
            self.s3_service.copy_across_bucket(
                self.staging_bucket_name,
                file_key,
                self.staging_bucket_name,
                destination_key,
            )
            return True
        except ClientError as e:
            logger.error(
                f"Failed to move metadata file '{file_key}' to '{destination_key}': {e}"
            )
            return False

    def generate_and_save_csv_file(
        self,
        csv_dict: list[dict],
        file_key: str,
    ):
        headers = csv_dict[0].keys() if csv_dict else []
        csv_data = convert_csv_dictionary_to_bytes(headers, csv_dict)
        logger.info(f"Writing file from buffer to {file_key}")
        self.s3_service.save_or_create_file(
            source_bucket=self.staging_bucket_name, file_key=file_key, body=csv_data
        )

    def update_date_in_row(self, metadata_row: dict):
        metadata_row["SCAN-DATE"] = metadata_row["SCAN-DATE"].replace(".", "/")
        metadata_row["UPLOAD"] = metadata_row["UPLOAD"].replace(".", "/")

        return metadata_row

    def validate_record_filename(self, file_name) -> str:
        try:
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
            file_name = self.assemble_valid_file_name(
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
            logger.info(f"Finished processing, new file name is: {file_name}")
            return file_name

        except InvalidFileNameException as error:
            logger.error(f"Failed to process {file_name} due to error: {error}")
            raise error

    def update_record_filename(self, original_row: dict, updated_row: dict):
        stripped_file_path = original_row.get("FILEPATH").lstrip("/")
        original_file_key = self.practice_directory + "/" + stripped_file_path
        new_file_key = updated_row.get("FILEPATH").lstrip("/")

        logger.info(f"Renaming file `{original_file_key}` to `{new_file_key}`")
        if original_file_key != new_file_key:
            try:
                self.s3_service.client.copy_object(
                    Bucket=self.staging_bucket_name,
                    CopySource={
                        "Bucket": self.staging_bucket_name,
                        "Key": original_file_key,
                    },
                    Key=new_file_key,
                )
            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                if error_code == "NoSuchKey":
                    error_message = "File doesn't exist on S3"
                    logger.info(f"{error_message} for `{original_file_key}`")
                    rejected_reason = {
                        "FILEPATH": original_row.get("FILEPATH"),
                        "REASON": error_message,
                    }
                    return None, original_row, rejected_reason
                else:
                    error_message = "Failed to create updated S3 filepath"
                    logger.error(f"{error_message} for `{original_file_key}`: {e}")
                    rejected_reason = {
                        "FILEPATH": original_row.get("FILEPATH"),
                        "REASON": error_message,
                    }
                    return None, original_row, rejected_reason
            try:
                self.s3_service.client.delete_object(
                    Bucket=self.staging_bucket_name, Key=original_file_key
                )
            except ClientError as e:
                error_message = "Failed to remove old S3 filepath"
                logger.error(f"error_message for `{original_file_key}`: {e}")
                rejected_reason = {
                    "FILEPATH": original_row.get("FILEPATH"),
                    "REASON": error_message,
                }
                return None, original_row, rejected_reason

        return updated_row, None, None

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
