import csv
import os
from datetime import datetime
from io import TextIOWrapper

import regex
from botocore.exceptions import ClientError
from models.staging_metadata import METADATA_FILENAME
from services.base.s3_service import S3Service
from six import BytesIO
from utils.audit_logging_setup import LoggingService
from utils.exceptions import InvalidFileNameException, MetadataPreprocessingException

logger = LoggingService(__name__)


class MetadataPreprocessorService:
    def __init__(self, practice_directory: str):
        self.s3_service = S3Service()
        self.staging_store_bucket = os.getenv("STAGING_STORE_BUCKET_NAME")
        self.processed_folder_name = "processed"
        self.practice_directory = practice_directory
        self.processed_date = datetime.now().strftime("%Y-%m-%d %H:%M")

    def process_metadata(self):
        file_key = f"{self.practice_directory}/{METADATA_FILENAME}"

        metadata_rows = self.get_metadata_rows_from_file(
            file_key=file_key, bucket_name=self.staging_store_bucket
        )

        logger.info("Processing metadata filenames")
        updated_metadata, rejected_list, error_list = self.standardize_filenames(
            metadata_rows
        )

        successfully_moved_file = self.move_original_metadata_file(file_key)
        if successfully_moved_file:
            self.s3_service.delete_object(
                s3_bucket_name=self.staging_store_bucket, file_key=file_key
            )

        logger.info("Generating buffered byte data from new csv data")
        metadata_headers = metadata_rows[0].keys() if metadata_rows else []
        updated_metadata_csv_buffer = self.convert_csv_dictionary_to_bytes(
            metadata_headers, updated_metadata
        )

        logger.info("Writing new metadata file from buffer")
        self.s3_service.save_or_create_file(
            self.staging_store_bucket, file_key, BytesIO(updated_metadata_csv_buffer)
        )

        # TODO Write rejected csv lines to a new failed.csv
        # and place this in the same subdirectory as the original processed metadata e.g. /processed
        # Prepare CSV in memory
        # csv_buffer = io.StringIO()

        # logger.info("Converting rejected list to a csv")
        # rejected_csv_buffer = self.convert_list_to_csv(
        #     metadata_csv_data[0].keys(), rejected_list
        # )
        # fieldnames = metadata_csv_data[0].keys() if metadata_csv_data else []
        #
        # writer = csv.DictWriter(csv_text_wrapper, fieldnames=fieldnames)
        # writer.writeheader()
        # writer.writerows(rejected_list)

        # Compose full key with folder
        # logger.info("Writing failure log from buffer")
        # failed_file_key = f"{self.practice_directory}/{self.processed_date}_failures_{METADATA_FILENAME}"
        # self.s3_service.save_or_create_file(
        #     self.staging_store_bucket, failed_file_key, rejected_csv_buffer
        # )

    def get_metadata_rows_from_file(self, file_key: str, bucket_name: str):
        logger.info(f"Retrieving {file_key}")
        file_exists = self.s3_service.file_exist_on_s3(
            s3_bucket_name=bucket_name, file_key=file_key
        )
        if not file_exists:
            logger.info(f"File {file_key} doesn't exist")
            raise MetadataPreprocessingException()

        response = self.s3_service.client.get_object(Bucket=bucket_name, Key=file_key)

        logger.info(f"Reading {file_key}")
        data = csv.DictReader(response["Body"].read().decode("utf-8").splitlines())
        metadata_rows = list(data)
        return metadata_rows

    def standardize_filenames(self, metadata_csv_data: list[dict]):
        logger.info("Standardizing filenames")

        updated_rows = []
        rejected_rows = []
        error_list = []

        for row in metadata_csv_data:
            original_file_name = row.get("FILEPATH")
            updated_row = row
            try:
                new_file_name = self.validate_record_filename(original_file_name)
                updated_row.update({"FILEPATH": new_file_name})
                updated_rows.append(updated_row)
                if new_file_name != original_file_name:
                    self.update_record_filename(original_file_name, new_file_name)
            except InvalidFileNameException as error:
                rejected_rows.append(row)
                error_list.append((original_file_name, str(error)))

        logger.info("Finished updating and standardizing filenames")
        return updated_rows, rejected_rows, error_list

    def validate_record_filename(self, file_name) -> str:
        try:
            logger.info(f"Processing file name {file_name}")

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
            day, month, year, current_file_name = (
                self.extract_date_from_bulk_upload_file_name(current_file_name)
            )
            file_extension = self.extract_file_extension_from_bulk_upload_file_name(
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
                file_extension,
            )
            logger.info(f"Finished processing, new file name is: {file_name}")
            return file_name

        except InvalidFileNameException as error:
            logger.info(f"Failed to process {file_name} due to error: {error}")
            raise error

    def update_record_filename(self, original_file_name: str, new_file_name: str):
        logger.info("Updating file name")
        original_file_key = f"{self.practice_directory}/{original_file_name}"
        new_file_key = f"{self.practice_directory}/{new_file_name}"

        file_exists = self.s3_service.file_exist_on_s3(
            s3_bucket_name=self.staging_store_bucket, file_key=original_file_key
        )
        if not file_exists:
            logger.info(f"File {original_file_key} doesn't exist")
            return

        logger.info(
            f"Copying file `{original_file_name}` to new file name `{new_file_name}`"
        )
        self.s3_service.client.copy_object(
            Bucket=self.staging_store_bucket,
            CopySource={"Bucket": self.staging_store_bucket, "Key": original_file_key},
            Key=new_file_key,
        )

        logger.info(f"Deleting original file with name {original_file_name}")
        self.s3_service.client.delete_object(
            Bucket=self.staging_store_bucket, Key=original_file_key
        )

    def move_original_metadata_file(self, file_key: str):
        destination_key = f"{self.practice_directory}/{self.processed_folder_name}/{self.processed_date}/{METADATA_FILENAME}"
        logger.info(f"Moving metadata file from {file_key} to {destination_key}")
        try:
            self.s3_service.copy_across_bucket(
                self.staging_store_bucket,
                file_key,
                self.staging_store_bucket,
                destination_key,
            )
            return True
        except ClientError as e:
            logger.error(
                f"Failed to move metadata file '{file_key}' to '{destination_key}': {e}"
            )
            return False

    @staticmethod
    def extract_person_name_from_bulk_upload_file_name(
        file_path: str,
    ) -> tuple[str, str]:
        document_number_expression = r"^.*?([\p{L}]+(?:[^\p{L}\d]+[\p{L}]+)*)(.*)"
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
        current_file_path = expression_result.group(5)

        if len(year) == 2:
            year = "20" + year

        if 1 <= int(day) >= 31 or 1 <= int(month) >= 12:
            logger.info("Failed to find date in file name")
            raise InvalidFileNameException("incorrect date format")

        return day, month, year, current_file_path

    @staticmethod
    def extract_file_extension_from_bulk_upload_file_name(
        file_path: str,
    ) -> str:
        file_extension_expression = r"(\.([^.]*))$"
        expression_result = regex.search(rf"{file_extension_expression}", file_path)

        if expression_result is None:
            logger.info("Failed to find a file extension")
            raise InvalidFileNameException("incorrect file extension format")

        file_extension = expression_result.group(1)

        return file_extension

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
        file_extension: str,
    ) -> str:
        return (
            f"{first_document_number}of{second_document_number}"
            f"_{lloyd_george_record}_"
            f"[{patient_name}]_"
            f"[{nhs_number}]_"
            f"[{day}-{month}-{year}]"
            f"{file_extension}"
        )

    # todo move to library or util file
    @staticmethod
    def convert_csv_dictionary_to_bytes(
        headers: list[str], metadata_csv_data: list[dict], encoding: str = "utf-8"
    ) -> bytes:
        csv_buffer = BytesIO()
        csv_text_wrapper = TextIOWrapper(csv_buffer, encoding=encoding, newline="")
        fieldnames = headers if headers else []

        writer = csv.DictWriter(csv_text_wrapper, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(metadata_csv_data)

        csv_text_wrapper.flush()
        csv_buffer.seek(0)

        result = csv_buffer.getvalue()
        csv_buffer.close()

        return result
