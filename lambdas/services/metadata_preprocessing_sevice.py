import regex
from utils.audit_logging_setup import LoggingService
from utils.exceptions import InvalidFileNameException

logger = LoggingService(__name__)


class MetadataPreprocessingService:
    # def __init__(self, strict_mode):

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

    def validate_and_update_bulk_uplodad_file_name(self, file_path) -> str:
        try:
            logger.info(f"processing file name {file_path}")

            firstDocumentNumber, secondDocumentNumber, current_file_path = (
                self.extract_document_number_bulk_upload_file_name(file_path)
            )
            lloyd_george_record, current_file_path = (
                self.extract_lloyd_george_record_from_bulk_upload_file_name(
                    current_file_path
                )
            )
            person_name, current_file_path = (
                self.extract_person_name_from_bulk_upload_file_name(current_file_path)
            )
            nhs_number, current_file_path = (
                self.extract_nhs_number_from_bulk_upload_file_name(current_file_path)
            )
            day, month, year = self.extract_date_from_bulk_upload_file_name(
                current_file_path
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
            logger.info(f"Failed to process {file_path} due to error: {error}")
            return file_path
