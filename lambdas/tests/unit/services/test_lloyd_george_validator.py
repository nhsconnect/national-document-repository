import pytest

from services.lloyd_george_validator import validate_lg_file_type, LGFileTypeException, LGFileNameException, LGInvalidFilesException, validate_file_name, check_for_duplicate_files, check_for_number_of_files_match_expected


def test_catching_error_when_file_type_not_pdf():
    with pytest.raises(LGFileTypeException):
        file_type = 'image/png'
        validate_lg_file_type(file_type)

def test_valid_file_type():
    try:
        file_type = 'application/pdf'
        validate_lg_file_type(file_type)
    except LGFileTypeException:
        assert False, 'One or more of the files do not match the required file type'

def test_invalid_file_name():
    with pytest.raises(LGFileNameException):
        file_name = 'bad_name'
        validate_file_name(file_name)

def test_valid_file_name():
    try:
        file_name = '1of1_Lloyd_George_Record_[Joe Bloggs]_[1111111111]_[25-12-2019].pdf'
        validate_file_name(file_name)
    except LGFileNameException:
        assert False, 'One or more of the files do not match naming convention'

def test_files_with_duplication():
    with pytest.raises(LGInvalidFilesException):
        lg_file_list = [
                '1of1_Lloyd_George_Record_[Joe Bloggs]_[1111111111]_[25-12-2019].pdf',
                '1of1_Lloyd_George_Record_[Joe Bloggs]_[1111111111]_[25-12-2019].pdf'
            ]
        check_for_duplicate_files(lg_file_list)

def test_files_without_duplication():
    try:
        lg_file_list = [
            '1of2_Lloyd_George_Record_[Joe Bloggs]_[1111111111]_[25-12-2019].pdf',
            '2of2_Lloyd_George_Record_[Joe Bloggs]_[1111111111]_[25-12-2019].pdf'
        ]
        check_for_duplicate_files(lg_file_list)
    except LGFileNameException:
        assert False, 'One or more of the files are not valid'

def test_files_list_with_missing_files():
    with pytest.raises(LGInvalidFilesException):
        lg_file_list = [
            '1of3_Lloyd_George_Record_[Joe Bloggs]_[1111111111]_[25-12-2019].pdf',
            '2of3_Lloyd_George_Record_[Joe Bloggs]_[1111111111]_[25-12-2019].pdf'
        ]
        check_for_number_of_files_match_expected(lg_file_list[0], str(len(lg_file_list)))

def test_files_without_missing_files():
    try:
        lg_file_list = [
            '1of2_Lloyd_George_Record_[Joe Bloggs]_[1111111111]_[25-12-2019].pdf',
            '2of2_Lloyd_George_Record_[Joe Bloggs]_[1111111111]_[25-12-2019].pdf'
        ]
        check_for_number_of_files_match_expected(lg_file_list[0], str(len(lg_file_list)))
    except LGFileNameException:
        assert False, 'One or more of the files are not valid'