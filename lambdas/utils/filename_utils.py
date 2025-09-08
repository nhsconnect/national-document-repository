import datetime
import os

from regex import regex

from utils.audit_logging_setup import LoggingService
from utils.exceptions import InvalidFileNameException

logger = LoggingService(__name__)


def extract_page_number(filename: str) -> int:
    """
    extract page number from Lloyd George file names

    example usage:
        filename = "123of456_Lloyd_George_Record_[Joe Bloggs]_[123456789]_[25-12-2019].pdf"
        extract_page_number(filename)

    result:
        123
    """
    pos_to_trim = filename.index("of")
    page_number_as_string = filename[0:pos_to_trim]
    return int(page_number_as_string)


def extract_total_pages(filename: str) -> int:
    """
    extract total page number from Lloyd George file names

    example usage:
        filename = "123of456_Lloyd_George_Record_[Joe Bloggs]_[123456789]_[25-12-2019].pdf"
        extract_total_pages(filename)

    result:
        456
    """
    start_pos = filename.index("of") + 2
    end_pos = filename.index("_")
    page_number_as_string = filename[start_pos:end_pos]
    return int(page_number_as_string)

def assemble_lg_valid_file_name_full_path(
    file_path_prefix: str,
    first_document_number: int,
    second_document_number: int,
    patient_name: str,
    nhs_number: str,
    date_object: datetime,
    file_extension: str,
) -> str:
    """
    Assembles a complete file path for a Lloyd George record file.

    This function constructs a valid file name by combining a file path prefix with
    details such as document numbers, patient name, NHS number, a specific date, and
    a file extension.

    Parameters:
    file_path_prefix: str
        The prefix or directory path where the file will be saved.
    first_document_number: int
        The current document number in a multi-document series.
    second_document_number: int
        The total number of documents in the series.
    patient_name: str
        The name of the patient to whom the record pertains.
    nhs_number: str
        The NHS number associated with the patient.
    date_object: datetime
        A datetime object representing the date associated with the record.
    file_extension: str
        The file extension to be appended to the file name.

    Returns:
    str
        Fully assembled file name including a path, details, and extension.
    """
    return (
        f"{file_path_prefix}"
        f"{first_document_number}of{second_document_number}"
        f"_Lloyd_George_Record_"
        f"[{patient_name}]_"
        f"[{nhs_number}]_"
        f"[{date_object.strftime("%d-%m-%Y")}]"
        f"{file_extension}"
    )


def extract_document_path(
    file_path: str,
) -> tuple[str, str]:

    directory_path, file_name = os.path.split(file_path)
    if not file_name:
        logger.info("Failed to find the document path in file name")
        raise InvalidFileNameException("Incorrect document path format")

    return directory_path, file_name

def extract_nhs_number_from_bulk_upload_file_name(
    file_path: str,
) -> tuple[str, str]:

    nhs_number_expression = r"((?:[^_]*?\d){10})(.*)"
    expression_result = regex.search(rf"{nhs_number_expression}", file_path)

    if expression_result is None:
        logger.info("Failed to find NHS number in file name")
        raise InvalidFileNameException("Invalid NHS number")

    nhs_number = "".join(regex.findall(r"\d", expression_result.group(1)))
    remaining_file_path = expression_result.group(2)

    return nhs_number, remaining_file_path

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

def extract_date_from_bulk_upload_file_name(file_path):
    date_expression = r"(\D*\d{1,2})[^\w\d]*(\w{3,}|\d{1,2})[^\w\d]*(\d{4})(.*)"
    expression_result = regex.search(date_expression, file_path)

    if not expression_result:
        raise InvalidFileNameException("Could not find a valid date in the filename.")

    try:
        day_str = "".join(regex.findall(r"\d+", expression_result.group(1)))
        month_part = expression_result.group(2)
        year_str = expression_result.group(3)
        remaining_file_path = expression_result.group(4)

        if month_part.isalpha():
            month = datetime.datetime.strptime(month_part, "%b").month
        else:
            month = int("".join(regex.findall(r"\d+", month_part)))

        day = int(day_str)
        year = int(year_str)

        date_object = datetime.date(year=year, month=month, day=day)
        return date_object, remaining_file_path
    except (ValueError, TypeError) as e:
        raise InvalidFileNameException(f"Failed to parse date from filename: {e}")


