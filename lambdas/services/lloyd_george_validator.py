import re

from lambdas.models.nhs_document_reference import NHSDocumentReference

class LGInvalidFilesException(Exception):
    pass

def validate_lg_file_type(file_type: str):
    if file_type != 'application/pdf':
        raise LGInvalidFilesException('One or more of the files do not match the required file type')

def validate_file_name(name: str):
    lg_regex = r'[0-9]+of[0-9]+_Lloyd_George_Record_\[[A-Za-z À-ÿ\-]+]_\[[0-9]{10}]_\[\d\d-\d\d-\d\d\d\d].pdf'
    if not re.fullmatch(lg_regex, name):
        raise LGInvalidFilesException('One or more of the files do not match naming convention')

def check_for_duplicate_files(file_list: list[str]):
    if len(file_list) > len(set(file_list)):
        raise LGInvalidFilesException('One or more of the files has the same filename')

def check_for_number_of_files_match_expected(file_name: str, total_files_number: int):
    lg_number_regex = 'of[0-9]+'
    expected_number_of_files = re.search(lg_number_regex, file_name)
    if expected_number_of_files and not expected_number_of_files.group()[2:] == str(total_files_number):
        raise LGInvalidFilesException('There are missing file(s) in the request')

def validate_lg_files(file_list: list[NHSDocumentReference]):
    for doc in file_list:
        validate_lg_file_type(doc.content_type)

    file_name_list = [doc.file_name for doc in file_list]
    validate_lg_file_names(file_name_list)


def validate_lg_file_names(file_name_list: list[str]):
    for file_name in file_name_list:
        check_for_number_of_files_match_expected(file_name, len(file_name_list))
        validate_file_name(file_name)
    check_for_duplicate_files(file_name_list)