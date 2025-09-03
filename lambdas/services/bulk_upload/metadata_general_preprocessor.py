from datetime import datetime

from regex import regex

from utils.audit_logging_setup import LoggingService
from utils.exceptions import InvalidFileNameException
from utils.filename_utils import assemble_lg_valid_file_name_full_path

logger = LoggingService(__name__)


class MetadataGeneralPreprocessor:
    def validate_record_filename(self, file_name) -> str:
        try:
            logger.info(f"Processing file name {file_name}")

            file_path_prefix, current_file_name = self.extract_document_path(file_name)
            first_document_number, second_document_number, current_file_name = (
                self.extract_document_number_bulk_upload_file_name(current_file_name)
            )
            current_file_name = (
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
            file_name = assemble_lg_valid_file_name_full_path(
                file_path_prefix,
                first_document_number,
                second_document_number,
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
    ) -> str:
        _expression = r".*?ll[oO0οՕ〇]yd.*?ge[oO0οՕ〇]rge.*?rec[oO0οՕ〇]rd(.*)"
        lloyd_george_record = regex.search(
            rf"{_expression}", file_path, regex.IGNORECASE
        )
        if lloyd_george_record is None:
            logger.info("Failed to extract Lloyd George Record from file name")
            raise InvalidFileNameException("Invalid Lloyd_George_Record separator")

        current_file_path = lloyd_george_record.group(1)


        return current_file_path


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
