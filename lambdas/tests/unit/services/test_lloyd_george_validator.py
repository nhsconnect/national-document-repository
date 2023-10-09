import pytest

from services.lloyd_george_validator import validate_lg_file_type, LGFileTypeException

def test_catching_error_when_file_type_not_pdf():
    with pytest.raises(LGFileTypeException):
        file_type = 'image/png'
        validate_lg_file_type(file_type)

def test_valid_file_type():
    try:
        file_type = 'application/pdf'
        validate_lg_file_type(file_type)
    except LGFileTypeException:
        assert False, 'One or more of the files do not match the required file type.'
