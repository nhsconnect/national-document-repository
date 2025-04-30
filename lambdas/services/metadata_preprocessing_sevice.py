import os

import regex
from models.staging_metadata import METADATA_FILENAME
from services.base.s3_service import S3Service
from utils.audit_logging_setup import LoggingService
from utils.exceptions import InvalidFileNameException

logger = LoggingService(__name__)


class MetadataPreprocessingService:
    def __init__(self):
        self.s3_service = S3Service()
        self.staging_store_bucket = os.getenv("STAGING_STORE_BUCKET_NAME")

    def extract_person_name_from_bulk_upload_file_name(self, file_path):
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

    def extract_lloyd_george_record_from_bulk_upload_file_name(self, file_path):

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

    def extract_document_number_bulk_upload_file_name(self, file_path):
        document_number_expression = r"[^0-9]*(\d+)[^0-9]*of[^0-9]*(\d+)(.*)"
        expression_result = regex.search(rf"{document_number_expression}", file_path)

        if expression_result is None:
            logger.info("Failed to find the document number in file name")
            raise InvalidFileNameException("incorrect document number format")

        firstDocumentNumber = int(expression_result.group(1))
        secondDocumentNumber = int(expression_result.group(2))
        current_file_path = expression_result.group(3)

        return firstDocumentNumber, secondDocumentNumber, current_file_path

    def extract_nhs_number_from_bulk_upload_file_name(self, file_path):
        nhs_number_expression = r"((?:.*?\d){10})(.*)"
        expression_result = regex.search(rf"{nhs_number_expression}", file_path)

        if expression_result is None:
            logger.info("Failed to find NHS number in file name")
            raise InvalidFileNameException("incorrect NHS number format")

        nhs_number = "".join(regex.findall(r"\d", expression_result.group(1)))
        current_file_path = expression_result.group(2)

        return nhs_number, current_file_path

    def extract_date_from_bulk_upload_file_name(self, file_path):
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

    def assemble_valid_file_name(
        self,
        firstDocumentNumber,
        secondDocumentNumber,
        lloyd_george_record,
        person_name,
        nhs_number,
        day,
        month,
        year,
    ):
        return (
            f"{firstDocumentNumber}of{secondDocumentNumber}"
            f"_{lloyd_george_record}_"
            f"[{person_name}]_"
            f"[{nhs_number}]_"
            f"[{day}-{month}-{year}]"
        )

    def validate_and_update_bulk_uplodad_file_name(self, file_name) -> str:
        try:
            logger.info(f"processing file name {file_name}")

            firstDocumentNumber, secondDocumentNumber, current_file_name = (
                self.extract_document_number_bulk_upload_file_name(file_name)
            )
            lloyd_george_record, current_file_name = (
                self.extract_lloyd_george_record_from_bulk_upload_file_name(
                    current_file_name
                )
            )
            person_name, current_file_name = (
                self.extract_person_name_from_bulk_upload_file_name(current_file_name)
            )
            nhs_number, current_file_name = (
                self.extract_nhs_number_from_bulk_upload_file_name(current_file_name)
            )
            day, month, year = self.extract_date_from_bulk_upload_file_name(
                current_file_name
            )
            file_name = self.assemble_valid_file_name(
                firstDocumentNumber,
                secondDocumentNumber,
                lloyd_george_record,
                person_name,
                nhs_number,
                day,
                month,
                year,
            )
            return file_name

        except InvalidFileNameException as error:
            logger.info(f"Failed to process {file_name} due to error: {error}")
            return file_name

    def process_metadata(self, practice_directory: str) -> str:
        # file_exist_on_s3(self, s3_bucket_name: str, file_key: str)
        file_key = f"{practice_directory}/{METADATA_FILENAME}"
        fileExists = self.s3_service.file_exist_on_s3(
            s3_bucket_name=self.staging_store_bucket, file_key=file_key
        )
        if fileExists:
            logger.info(f"File {file_key} already exists")
        # else:
        # bulk_upload_report_service().csv_to_staging_metadata(file_key)
        # self.csv_to_staging_metadata_with_updated_file_names(file_key)

    #
    # @staticmethod
    # def csv_to_staging_metadata_with_updated_file_names(csv_file_path: str) -> list[StagingMetadata]:
    #     logger.info("Parsing bulk upload metadata")
    #
    #     patients = {}
    #     with open(
    #             csv_file_path, mode="r", encoding="utf-8", errors="replace"
    #     ) as csv_file_handler:
    #         csv_reader: Iterable[dict] = csv.DictReader(csv_file_handler)
    #         for row in csv_reader:
    #             file_metadata = MetadataFile.model_validate(row)
    #             # MetadataFile.file_path = self.validate_and_update_bulk_uplodad_file_name(file_path=MetadataFile.file_path)
    #             # nhs_number = row[NHS_NUMBER_FIELD_NAME]
    #             # row.file_name = file_metadata.file_name
    #             row.file_name = validate_and_update_bulk_uplodad_file_name(file_metadata.file_name)
    #             # if nhs_number not in patients:
    #             #     patients[nhs_number] = [file_metadata]
    #             # else:
    #             #     patients[nhs_number] += [file_metadata]
    #
    #     return [
    #         StagingMetadata(nhs_number=nhs_number, files=patients[nhs_number])
    #         for nhs_number in patients
    #     ]
