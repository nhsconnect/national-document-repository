import csv
import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
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

        logger.info("Generating renaming map from metadata")
        renaming_map, rejected_rows, rejected_reasons = self.generate_renaming_map(
            metadata_rows
        )

        logger.info("Processing metadata filenames")
        updated_metadata_rows = self.standardize_filenames(renaming_map)

        successfully_moved_file = self.move_original_metadata_file(file_key)
        if successfully_moved_file:
            self.s3_service.delete_object(
                s3_bucket_name=self.staging_store_bucket, file_key=file_key
            )

        self.generate_and_save_csv_file(updated_metadata_rows, file_key)

        if rejected_reasons:
            file_key = f"{self.practice_directory}/{self.processed_folder_name}/{self.processed_date}/rejections.csv"
            self.generate_and_save_csv_file(rejected_reasons, file_key)

    def generate_and_save_csv_file(
        self,
        csv_dict: list[dict],
        file_key: str,
    ):
        headers = csv_dict[0].keys() if csv_dict else []
        csv_data = self.convert_csv_dictionary_to_bytes(headers, csv_dict)
        logger.info(f"Writing file from buffer to {file_key}")
        self.s3_service.save_or_create_file(
            self.staging_store_bucket, file_key, BytesIO(csv_data)
        )

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

    def standardize_filenames(
        self, renaming_map: list[tuple[dict, dict]], max_workers=20
    ):
        logger.info("Standardizing filenames")

        updated_rows = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self.update_record_filename, original_row, updated_row)
                for original_row, updated_row in renaming_map
            ]

            for future in as_completed(futures):
                updated_row = future.result()
                if updated_row:
                    updated_rows.append(updated_row)

        logger.info("Finished updating and standardizing filenames")
        return updated_rows

    # def process_metadata_row(self, original_row: dict, updated_row: dict):
    #     try:
    #         original_file_name = original_row.get("FILEPATH")
    #         new_file_name = updated_row.get("FILEPATH")
    #
    #         if original_file_name != new_file_name:
    #             self.update_record_filename(original_file_name, new_file_name)
    #         return True, updated_row, None
    #     except InvalidFileNameException as error:
    #         return False, original_row, str(error)

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
                self.extract_person_name_from_bulk_upload_file_name(current_file_name)
            )

            if sum(c.isdigit() for c in current_file_name) != 18:
                logger.info("Failed to find NHS or date")
                raise InvalidFileNameException("incorrect NHS number or date format")

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

    def generate_renaming_map(self, metadata_rows: list[dict]):
        duplicate_counts = defaultdict(int)
        renaming_map = []
        rejected_rows = []
        rejected_reasons = []

        for original_row in metadata_rows:
            renamed_row = original_row.copy()

            original_filename = original_row.get("FILEPATH")

            try:
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
                rejected_reasons.append(
                    {"FILEPATH": original_row.get("FILEPATH"), "REASON": error}
                )

        return renaming_map, rejected_rows, rejected_reasons

    def update_record_filename(self, original_row: dict, updated_row: dict):
        stripped_file_path = original_row.get("FILEPATH").lstrip("/")
        original_file_key = self.practice_directory + "/" + stripped_file_path
        new_file_key = updated_row.get("FILEPATH").lstrip("/")

        logger.info(f"Renaming file `{original_file_key}` to `{new_file_key}`")
        if original_file_key != new_file_key:
            try:
                self.s3_service.client.copy_object(
                    Bucket=self.staging_store_bucket,
                    CopySource={
                        "Bucket": self.staging_store_bucket,
                        "Key": original_file_key,
                    },
                    Key=new_file_key,
                )
            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                if error_code == "NoSuchKey":
                    logger.info(f"File {original_file_key} doesn't exist")
                    return None
                else:
                    logger.error(
                        f"Failed update filename for `{original_file_key}`: {e}"
                    )
                    return None

            self.s3_service.client.delete_object(
                Bucket=self.staging_store_bucket, Key=original_file_key
            )

        return updated_row

    def move_original_metadata_file(self, file_key: str):
        destination_key = f"{self.practice_directory}/{self.processed_folder_name}/{self.processed_date}/{METADATA_FILENAME}"
        logger.info(
            f"Moving original metadata file from {file_key} to {destination_key}"
        )
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
        document_number_expression = r".*?([\p{L}][^\d]*[\p{L}])(.*)"
        expression_result = regex.search(
            rf"{document_number_expression}", file_path, regex.IGNORECASE
        )

        if expression_result is None:
            logger.info("Failed to find the person name in the file name")
            raise InvalidFileNameException("incorrect person name format")

        name = expression_result.group(1)
        current_file_path = expression_result.group(2)

        return name, current_file_path

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
    def extract_document_path(
        file_path: str,
    ) -> tuple[str, str]:
        document_number_expression = r"(.*[/])*((\d+)[^0-9]*of[^0-9]*(\d+)(.*))"

        expression_result = regex.search(rf"{document_number_expression}", file_path)

        if expression_result is None:
            logger.info("Failed to find the document number in file name")
            raise InvalidFileNameException("incorrect document number format")

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
            raise InvalidFileNameException("incorrect NHS number format")

        nhs_number = "".join(regex.findall(r"\d", expression_result.group(1)))
        current_file_path = expression_result.group(2)

        return nhs_number, current_file_path

    @staticmethod
    def extract_date_from_bulk_upload_file_name(file_path):
        date_number_expression = r"(\D+\d{2})(\D*\d{2})(\D*(\d{4}))(.*)"
        expression_result = regex.search(rf"{date_number_expression}", file_path)

        if expression_result is None:
            logger.info("Failed to find date in file name")
            raise InvalidFileNameException("incorrect date format")

        day = "".join(regex.findall(r"\d", expression_result.group(1))).zfill(2)
        month = "".join(regex.findall(r"\d", expression_result.group(2))).zfill(2)
        year = "".join(regex.findall(r"\d", expression_result.group(3)))
        current_file_path = expression_result.group(5)

        try:
            datetime(day=int(day), month=int(month), year=int(year))
        except ValueError:
            logger.info("Failed to find date in file name")
            raise InvalidFileNameException("not a valid date")

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

    # todo move to library or util file
    @staticmethod
    def convert_csv_dictionary_to_bytes(
        headers: list[str], csv_dict_data: list[dict], encoding: str = "utf-8"
    ) -> bytes:
        csv_buffer = BytesIO()
        csv_text_wrapper = TextIOWrapper(csv_buffer, encoding=encoding, newline="")
        fieldnames = headers if headers else []

        writer = csv.DictWriter(csv_text_wrapper, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_dict_data)

        csv_text_wrapper.flush()
        csv_buffer.seek(0)

        result = csv_buffer.getvalue()
        csv_buffer.close()

        return result
