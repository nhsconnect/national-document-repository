import pytest

from services.lloyd_george_validator import validate_lg_file_type, LGFileTypeException, LGFileNameException, validate_file_name

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
