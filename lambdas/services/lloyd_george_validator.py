import re
from typing import Optional

from models.nhs_document_reference import NHSDocumentReference


class LGInvalidFilesException(Exception):
    pass


def validate_lg_file_type(file_type: str):
    if file_type != "application/pdf":
        raise LGInvalidFilesException(
            "One or more of the files do not match the required file type"
        )


def validate_file_name(name: str):
    lg_regex = r"[0-9]+of[0-9]+_Lloyd_George_Record_\[[A-Za-z À-ÿ\-]+]_\[[0-9]{10}]_\[\d\d-\d\d-\d\d\d\d].pdf"
    if not re.fullmatch(lg_regex, name):
        raise LGInvalidFilesException(
            "One or more of the files do not match naming convention"
        )


def check_for_duplicate_files(file_list: list[str]):
    if len(file_list) > len(set(file_list)):
        raise LGInvalidFilesException("One or more of the files has the same filename")


def check_for_number_of_files_match_expected(file_name: str, total_files_number: int):
    lg_number_regex = "of[0-9]+"
    expected_number_of_files = re.search(lg_number_regex, file_name)
    if expected_number_of_files and not expected_number_of_files.group()[2:] == str(
        total_files_number
    ):
        raise LGInvalidFilesException("There are missing file(s) in the request")


def validate_lg_files(file_list: list[NHSDocumentReference]):
    files_name_list = []
    for doc in file_list:
        check_for_number_of_files_match_expected(doc.file_name, len(file_list))
        validate_lg_file_type(doc.content_type)
        validate_file_name(doc.file_name)
        files_name_list.append(doc.file_name)
    check_for_duplicate_files(files_name_list)


def validate_lg_file_names(file_name_list: list[str], nhs_number: Optional[str] = None):
    for file_name in file_name_list:
        check_for_number_of_files_match_expected(file_name, len(file_name_list))
        validate_file_name(file_name)
    check_for_duplicate_files(file_name_list)
    check_for_file_names_agrees_with_each_other(file_name_list)

    if nhs_number:
        # Check file names match with the nhs number in metadata.csv
        file_name_info = extract_info_from_filename(file_name_list[0])
        if file_name_info["nhs_number"] != nhs_number:
            raise LGInvalidFilesException(
                "NHS number in file names does not match the given NHS number"
            )


def extract_info_from_filename(filename: str) -> dict:
    page_number = r"(?P<page_no>[1-9][0-9]*)"
    total_page_number = r"(?P<total_page_no>[1-9][0-9]*)"
    patient_name = r"(?P<patient_name>[A-Za-z À-ÿ\-]+)"
    nhs_number = r"(?P<nhs_number>\d{10})"
    date_of_birth = r"(?P<dob>\d\d-\d\d-\d\d\d\d)"

    # ruff: noqa: E501
    lg_regex = rf"{page_number}of{total_page_number}_Lloyd_George_Record_\[{patient_name}\]_\[{nhs_number}\]_\[{date_of_birth}\].pdf"

    if match := re.fullmatch(lg_regex, filename):
        return match.groupdict()
    else:
        raise LGInvalidFilesException(
            "One or more of the files do not match naming convention"
        )


def check_for_file_names_agrees_with_each_other(file_name_list: list[str]):
    expected_common_part = [
        file_name[file_name.index("of") :] for file_name in file_name_list
    ]
    if len(set(expected_common_part)) != 1:
        raise LGInvalidFilesException("File names does not match with each other")
