import re

from lambdas.models.nhs_document_reference import NHSDocumentReference


class LGFileTypeException(ValueError):
    """One or more of the files do not match the required file type"""
    pass

class LGFileNameException(ValueError):
    """One or more of the files do not match naming convention"""
    pass

class LGInvalidFilesException(Exception):
    """One or more of the files are not valid"""
    pass

def validate_lg_file_type(file_type: str):
    if file_type != 'application/pdf':
        raise LGFileTypeException

def validate_file_name(name: str):
    lg_regex = r'[0-9]+of[0-9]+_Lloyd_George_Record_\[[A-Za-z ]+]_\[[0-9]{10}]_\[\d\d-\d\d-\d\d\d\d].pdf'
    if not re.fullmatch(lg_regex, name):
        raise LGFileNameException

def check_for_duplicate_files(file_list: list[str]):
    if len(file_list) > len(set(file_list)):
        raise LGInvalidFilesException

def check_for_number_of_files_match_expected(file_name: str, total_files_number: int):
    lg_number_regex = 'of[0-9]+'
    expected_number_of_files = re.search(lg_number_regex, file_name)
    if expected_number_of_files and not expected_number_of_files.group()[2:] == str(total_files_number):
        raise LGInvalidFilesException

def validate_lg_files(file_list: list[NHSDocumentReference]):
    files_name_list = []
    for doc in file_list:
        check_for_number_of_files_match_expected(doc.file_name, len(file_list))
        validate_lg_file_type(doc.content_type)
        validate_file_name(doc.file_name)
        files_name_list.append(doc.file_name)
    check_for_duplicate_files(files_name_list)
