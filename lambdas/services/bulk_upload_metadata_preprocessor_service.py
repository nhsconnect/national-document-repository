import csv
import os
from io import TextIOWrapper

import regex
from models.staging_metadata import METADATA_FILENAME
from services.base.s3_service import S3Service
from six import BytesIO
from utils.audit_logging_setup import LoggingService
from utils.exceptions import InvalidFileNameException, MetadataPreprocessingException

logger = LoggingService(__name__)


class MetadataPreprocessingService:
    def __init__(self, practice_directory: str):
        self.s3_service = S3Service()
        self.staging_store_bucket = os.getenv("STAGING_STORE_BUCKET_NAME")
        self.processed_folder_name = "/processed"
        self.practice_directory = practice_directory

    @staticmethod
    def extract_person_name_from_bulk_upload_file_name(
        file_path: str,
    ) -> tuple[str, str]:
        document_number_expression = r".*?([\p{L}]+(?:[^\p{L}]+[\p{L}]+)*)(.*)$"
        expression_result = regex.search(
            rf"{document_number_expression}", file_path, regex.IGNORECASE
        )
        if expression_result is None:
            logger.info("Failed to find the person name in the file name")
            raise InvalidFileNameException("incorrect person name format")

        name = expression_result.group(1)

        # Replace all non-letter characters (except spaces) with a space
        cleaned_name = regex.sub(r"[^\p{L}]", " ", name)

        # Replace multiple spaces with a single space
        cleaned_name = regex.sub(r"\s+", " ", cleaned_name).strip()

        # Camel case name
        cleaned_name = " ".join(word.capitalize() for word in cleaned_name.split())
        current_file_path = expression_result.group(2)

        return cleaned_name, current_file_path

    @staticmethod
    def extract_lloyd_george_record_from_bulk_upload_file_name(
        file_path: str,
    ) -> tuple[str, str]:
        _expression = r".*?ll[oO0οՕ〇]yd.*?ge[oO0οՕ〇]rge.*?rec[oO0οՕ〇]rd(.*)"
        lloyd_george_record = regex.search(
            rf"{_expression}", file_path, regex.IGNORECASE
        )
        if lloyd_george_record is None:
            logger.info("Failed to find Lloyd George Record")
            raise InvalidFileNameException("incorrect Lloyd George Record format")

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
            raise InvalidFileNameException("incorrect document number format")

        first_document_number = int(expression_result.group(1))
        second_document_number = int(expression_result.group(2))
        current_file_path = expression_result.group(3)

        return first_document_number, second_document_number, current_file_path

    @staticmethod
    def extract_nhs_number_from_bulk_upload_file_name(
        file_path: str,
    ) -> tuple[str, str]:
        nhs_number_expression = r"((?:.*?\d){10})(.*)"
        expression_result = regex.search(rf"{nhs_number_expression}", file_path)

        if expression_result is None:
            logger.info("Failed to find NHS number in file name")
            raise InvalidFileNameException("incorrect NHS number format")

        nhs_number = "".join(regex.findall(r"\d", expression_result.group(1)))
        current_file_path = expression_result.group(2)

        return nhs_number, current_file_path

    @staticmethod
    def extract_date_from_bulk_upload_file_name(file_path):
        date_number_expression = r"(\D*\d{1,2})(\D*\d{1,2})(\D*(\d{4}|\d{2}))(.*)"
        expression_result = regex.search(rf"{date_number_expression}", file_path)

        if expression_result is None:
            logger.info("Failed to find date in file name")
            raise InvalidFileNameException("incorrect date format")

        day = "".join(regex.findall(r"\d", expression_result.group(1))).zfill(2)
        month = "".join(regex.findall(r"\d", expression_result.group(2))).zfill(2)
        year = "".join(regex.findall(r"\d", expression_result.group(3)))
        if len(year) == 2:
            year = "20" + year

        if 1 <= int(day) >= 31 or 1 <= int(month) >= 12:
            logger.info("Failed to find date in file name")
            raise InvalidFileNameException("incorrect date format")

        return day, month, year

    @staticmethod
    def assemble_valid_file_name(
        first_document_number: int,
        second_document_number: int,
        lloyd_george_record: str,
        patient_name: str,
        nhs_number: str,
        day: str,
        month: str,
        year: str,
    ) -> str:
        return (
            f"{first_document_number}of{second_document_number}"
            f"_{lloyd_george_record}_"
            f"[{patient_name}]_"
            f"[{nhs_number}]_"
            f"[{day}-{month}-{year}]"
        )

    def validate_and_update_file_name(self, file_name) -> str:
        try:
            logger.info(f"processing file name {file_name}")

            first_document_number, second_document_number, current_file_name = (
                self.extract_document_number_bulk_upload_file_name(file_name)
            )
            lloyd_george_record, current_file_name = (
                self.extract_lloyd_george_record_from_bulk_upload_file_name(
                    current_file_name
                )
            )
            patient_name, current_file_name = (
                self.extract_person_name_from_bulk_upload_file_name(current_file_name)
            )
            nhs_number, current_file_name = (
                self.extract_nhs_number_from_bulk_upload_file_name(current_file_name)
            )
            day, month, year = self.extract_date_from_bulk_upload_file_name(
                current_file_name
            )
            file_name = self.assemble_valid_file_name(
                first_document_number,
                second_document_number,
                lloyd_george_record,
                patient_name,
                nhs_number,
                day,
                month,
                year,
            )
            return file_name

        except InvalidFileNameException as error:
            logger.info(f"Failed to process {file_name} due to error: {error}")
            return file_name

    def process_metadata(
        self,
    ):
        file_key = f"{self.practice_directory}/{METADATA_FILENAME}"
        file_exists = self.s3_service.file_exist_on_s3(
            s3_bucket_name=self.staging_store_bucket, file_key=file_key
        )

        if not file_exists:
            logger.info(f"File {file_key} doesn't exist")
            raise MetadataPreprocessingException()

        response = self.s3_service.client.get_object(
            Bucket=self.staging_store_bucket, Key=file_key
        )

        metadata_csv = csv.DictReader(
            response["Body"].read().decode("utf-8").splitlines()
        )
        metadata_csv_data = list(metadata_csv)

        print(metadata_csv_data)

        # TODO update file names
        metadata_csv_data, rejected_list, error_list = (
            self.update_and_standardize_filenames(metadata_csv_data)
        )

        # Convert list of dicts to CSV in memory
        # use bites.io
        csv_buffer = BytesIO()
        csv_text_wrapper = TextIOWrapper(csv_buffer, encoding="utf-8", newline="")
        fieldnames = metadata_csv_data[0].keys() if metadata_csv_data else []

        writer = csv.DictWriter(csv_text_wrapper, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(metadata_csv_data)

        csv_text_wrapper.flush()
        csv_buffer.seek(0)

        # TODO Move original metadata file into subdirectory for process files e.g. /processed
        self.move_original_metadata_file(file_key)

        self.s3_service.save_or_create_file(
            file_key, file_key, BytesIO(csv_text_wrapper.buffer.read())
        )
        # self.s3_service.client.put_object(
        #     Bucket=source_bucket,
        #     Key=file_key,
        #     Body=csv_buffer.getvalue()
        # )
        # TODO Write rejected csv lines to a new failed.csv
        # and place this in the same subdirectory as the original processed metadata e.g. /processed
        # Prepare CSV in memory
        # csv_buffer = io.StringIO()
        fieldnames = metadata_csv_data[0].keys() if metadata_csv_data else []

        writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rejected_list)

        # Compose full key with folder
        failed_file_key = f"{self.practice_directory}/failed{METADATA_FILENAME}"
        self.s3_service.save_or_create_file(
            file_key, failed_file_key, csv_buffer.getvalue()
        )
        # Upload to S3
        # self.s3_service.client.put_object(
        #     Bucket=source_bucket,
        #     Key=failed_file_key,
        #     Body=csv_buffer.getvalue()
        # )

        response = self.s3_service.client.upload_fileobj(
            Fileobj=BytesIO(), Bucket=self.staging_store_bucket, Key=file_key
        )

    def update_and_standardize_filenames(self, metadata_csv_data):
        rejected_list = []
        error_list = []
        for row in metadata_csv_data:
            try:
                new_filepath = self.validate_and_update_file_name(row.get("FILEPATH"))
                row["FILEPATH"] = new_filepath
            except MetadataPreprocessingException as error:
                rejected_list.append(row.get("FILEPATH"))
                error_list.append((row.get("FILEPATH"), str(error)))
        return metadata_csv_data, rejected_list, error_list

    def move_original_metadata_file(self, file_key: str):
        destination_key = f"{self.practice_directory}/{self.processed_folder_name}/{METADATA_FILENAME}"

        self.s3_service.client.move_file_in_bucket(
            self.staging_store_bucket, file_key, destination_key
        )
