import datetime
import os

from regex import regex

from utils.audit_logging_setup import LoggingService
from utils.exceptions import InvalidFileNameException

logger = LoggingService(__name__)


def extract_page_number(filename: str) -> int:
    """
    Extracts the page number from a Lloyd George file name.

    Args:
        filename (str): The file name to extract the page number from.

    Returns:
        int: The extracted page number.

    Raises:
        ValueError: If the extracted page number cannot be converted to an integer.

    Example:
        filename = "123of456_Lloyd_George_Record_[Joe Bloggs]_[123456789]_[25-12-2019].pdf"
        extract_page_number(filename) -> 123
    """
    pos_to_trim = filename.index("of")
    page_number_as_string = filename[0:pos_to_trim]
    return int(page_number_as_string)


def extract_total_pages(filename: str) -> int:
    """
    Extracts the total number of pages from a Lloyd George file name.

    Args:
        filename (str): The file name to extract the total pages from.

    Returns:
        int: The extracted total number of pages.

    Raises:
        ValueError: If the extracted total pages cannot be converted to an integer.

    Example:
        filename = "123of456_Lloyd_George_Record_[Joe Bloggs]_[123456789]_[25-12-2019].pdf"
        extract_total_pages(filename) -> 456
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
    date_object: datetime.date,
    file_extension: str,
) -> str:
    """
    Assembles a complete file path for a Lloyd George record file.

    Args:
        file_path_prefix (str): The directory path where the file will be saved.
        first_document_number (int): The current document number in a series.
        second_document_number (int): The total number of documents in the series.
        patient_name (str): The name of the patient.
        nhs_number (str): The NHS number of the patient.
        date_object (datetime.date): The date associated with the record.
        file_extension (str): The file extension to append.

    Returns:
        str: The fully assembled file name including the path and details.

    Example:
        folder_path/1of2_Lloyd_George_Record_[Joe Bloggs]_[123456789]_[25-12-2019].pdf
    """
    return (
        f"{file_path_prefix}{first_document_number}of{second_document_number}"
        f"_Lloyd_George_Record_[{patient_name}]_[{nhs_number}]_"
        f"[{date_object.strftime('%d-%m-%Y')}]{file_extension}"
    )


def extract_document_path(
    file_path: str,
) -> tuple[str, str]:
    """
    Extracts the directory path and file name from a given file path.

    Args:
        file_path (str): The full file path.

    Returns:
        tuple[str, str]: A tuple containing the directory path and file name.

    Raises:
        InvalidFileNameException: If the file name is missing.
    """
    directory_path, file_name = os.path.split(file_path)
    if not file_name:
        logger.info("Failed to find the document path in file name")
        raise InvalidFileNameException("Incorrect document path format")

    return directory_path, file_name


def extract_nhs_number_from_bulk_upload_file_name(
    file_path: str,
) -> tuple[str, str]:
    """
    Extracts the NHS number from a bulk upload file name.

    Args:
        file_path (str): The file path to extract the NHS number from.

    Returns:
        tuple[str, str]: A tuple containing the NHS number and the remaining file path.

    Raises:
        InvalidFileNameException: If the NHS number is invalid or not found.
    """
    nhs_number_expression = r"(?<!\d)((?:[^\d_]*\d){10})(?!\d)(.*)"
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
    """
    Extracts the patient name from a bulk upload file name.

    Args:
        file_path (str): The file path to extract the patient name from.

    Returns:
        tuple[str, str]: A tuple containing the patient name and the remaining file path.

    Raises:
        InvalidFileNameException: If the patient name is invalid or not found.
    """
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
    """
    Extracts the date from a bulk upload file name.

    Args:
        file_path (str): The file path to extract the date from.

    Returns:
        tuple[datetime.date, str]: A tuple containing the extracted date as a datetime.date object and the remaining file path.

    Raises:
        InvalidFileNameException: If the date is invalid or not found.
    """
    date_expression = r"(\D+\d{1,2})[^\w\d]*(\w{3,}|\d{1,2})[^\w\d]*(\d{4})(.*)"
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
        logger.error(f"Failed to parse date from filename: {e}")
        raise InvalidFileNameException("Invalid date format")


def extract_document_path_for_lloyd_george_record(
    file_path: str,
) -> tuple[str, str]:
    """
    Extracts the document path for a Lloyd George record from a file path.

    Args:
        file_path (str): The file path to extract the document path from.

    Returns:
        tuple[str, str]: A tuple containing the directory path and the file name.

    Raises:
        InvalidFileNameException: If the document path format is incorrect.

    Example:
        file_path=folder_path/1of2_Lloyd_George_Record.pdf
        extract_document_path_for_lloyd_george_record(file_path) -> folder_path/, 1of2_Lloyd_George_Record.pdf
    """
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


def extract_document_number_bulk_upload_file_name(
    file_path: str,
) -> tuple[int, int, str]:
    """
    Extracts the document number and total document count from the file name.

    Args:
        file_path (str): The file path to extract the document numbers from.

    Returns:
        tuple[int, int, str]: A tuple containing the current document number, total document count, and the remaining file path.

    Raises:
        InvalidFileNameException: If the document number format is incorrect.

    Example:
        file_path=1of2_Lloyd_George_Record_[Joe Bloggs]_[123456789]_[25-12-2019].pdf
        extract_document_number_bulk_upload_file_name(file_path) ->
        1, 2, _Lloyd_George_Record_[Joe Bloggs]_[123456789]_[25-12-2019].pdf
    """
    document_number_expression = r"[^0-9]*(\d+)[^0-9]*of[^0-9]*(\d+)(.*)"
    expression_result = regex.search(rf"{document_number_expression}", file_path)

    if expression_result is None:
        logger.info("Failed to find the document number in file name")
        raise InvalidFileNameException("Incorrect document number format")

    current_document_number = int(expression_result.group(1))
    expected_total_document_number = int(expression_result.group(2))
    current_file_path = expression_result.group(3)

    return current_document_number, expected_total_document_number, current_file_path


def extract_lloyd_george_record_from_bulk_upload_file_name(
    file_path: str,
) -> str:
    """
    Remove 'Lloyd_George_Record' from the file name.

    Args:
        file_path (str): The file path to extract the Lloyd George record from.

    Returns:
        str: The remaining file path after extracting the Lloyd George record.

    Raises:
        InvalidFileNameException: If the Lloyd George record separator is invalid.

    Example:
        file_path=1of2_Lloyd_George_Record_[Joe Bloggs]_[123456789]_[25-12-2019].pdf
        extract_lloyd_george_record_from_bulk_upload_file_name(file_path) -> _[Joe Bloggs]_[123456789]_[25-12-2019].pdf
    """
    _expression = r".*?ll[oO0οՕ〇]yd.*?ge[oO0οՕ〇]rge.*?rec[oO0οՕ〇]rd(.*)"
    lloyd_george_record = regex.search(rf"{_expression}", file_path, regex.IGNORECASE)
    if lloyd_george_record is None:
        logger.info("Failed to extract Lloyd George Record from file name")
        raise InvalidFileNameException("Invalid Lloyd_George_Record separator")

    current_file_path = lloyd_george_record.group(1)

    return current_file_path


def extract_file_extension_from_bulk_upload_file_name(
    file_path: str,
) -> str:
    """
    Extracts the file extension from a bulk upload file name.

    Args:
        file_path (str): The file path to extract the file extension from.

    Returns:
        str: The extracted file extension.

    Raises:
        InvalidFileNameException: If the file extension is invalid or not found.
    """
    file_extension_expression = r"(\.([^.]*))$"
    expression_result = regex.search(rf"{file_extension_expression}", file_path)

    if expression_result is None:
        logger.info("Failed to find a file extension")
        raise InvalidFileNameException("Invalid file extension")

    file_extension = expression_result.group(1)

    return file_extension
