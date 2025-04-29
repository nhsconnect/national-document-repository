import regex
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class MetadataPreprocessingService:
    # def __init__(self, strict_mode):

    def extract_person_name_from_bulk_upload_file_name(self, file_path):
        document_number_expression = r".*?([\p{L}]+(?:[^\p{L}]+[\p{L}]+)*)(.*)$"
        document_number = regex.search(
            rf"{document_number_expression}", file_path, regex.IGNORECASE
        )

        name = document_number.group(1)

        # Replace all non-letter characters (except spaces) with a space
        cleaned_name = regex.sub(r"[^\p{L}]", " ", name)

        # Replace multiple spaces with a single space
        cleaned_name = regex.sub(r"\s+", " ", cleaned_name).strip()

        # Camel case name
        cleaned_name = " ".join(word.capitalize() for word in cleaned_name.split())
        current_file_path = document_number.group(2)

        return cleaned_name, current_file_path

    def extract_lloyd_george_record_from_bulk_upload_file_name(self, file_path):
        document_number_expression = r".*?lloyd.*?george.*?record(.*)"
        document_number = regex.search(
            rf"{document_number_expression}", file_path, regex.IGNORECASE
        )

        current_file_path = document_number.group(1)

        lloyd_george_record = "Lloyd_George_Record"

        return lloyd_george_record, current_file_path

    def extract_document_number_bulk_upload_file_name(self, file_path):
        document_number_expression = r"[^0-9]*(\d+)[^0-9]*of[^0-9]*(\d+)(.*)"
        document_number = regex.search(rf"{document_number_expression}", file_path)

        firstDocumentNumber = int(document_number.group(1))
        secondDocumentNumber = int(document_number.group(2))
        current_file_path = document_number.group(3)

        return firstDocumentNumber, secondDocumentNumber, current_file_path

    def extract_nhs_number_from_bulk_upload_file_name(self, file_path):
        nhs_number_expression = r"((?:.*?\d){10})(.*)"
        expression_result = regex.search(rf"{nhs_number_expression}", file_path)

        nhs_number = "".join(regex.findall(r"\d", expression_result.group(1)))
        current_file_path = expression_result.group(2)

        return nhs_number, current_file_path

    def extract_date_from_bulk_upload_file_name(self, file_path):
        date_number_expression = r"(\D*\d{1,2})(\D*\d{1,2})(\D*\d{4})(.*)"
        expression_result = regex.search(rf"{date_number_expression}", file_path)

        day = "".join(regex.findall(r"\d", expression_result.group(1))).zfill(2)
        month = "".join(regex.findall(r"\d", expression_result.group(2))).zfill(2)
        year = "".join(regex.findall(r"\d", expression_result.group(3)))

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
        # try:
        #     logger.info(f"processing file name {file_path}")

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

    # except (InvalidFileNameException) as error:
    #     self.unhandled_messages.append(message)
    #     logger.info(f"Failed to process current message due to error: {error}")
