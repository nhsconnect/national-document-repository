import pytest
from services.bulk_upload.metadata_usb_preprocessor import (
    MetadataUsbPreprocessorService,
)
from utils.exceptions import InvalidFileNameException


@pytest.fixture()
def test_service(set_env):
    service = MetadataUsbPreprocessorService()
    return service


@pytest.mark.parametrize(
    "file_path, expected",
    [
        (
            "/9876543210 Test Patient Name 01-Jan-2022/guid_unknown.pdf",
            "/9876543210 Test Patient Name 01-Jan-2022/1of1_Lloyd_George_Record_[Test Patient Name]_[9876543210]_[01-01-2022].pdf",
        ),
        (
            "/1234567890 Test Patient With A Very Long Name 01-Jan-2022/guid_unknown.pdf",
            "/1234567890 Test Patient With A Very Long Name 01-Jan-2022/1of1_Lloyd_George_Record_[Test Patient With A Very Long Name]_[1234567890]_[01-01-2022].pdf",
        ),
        (
            "/9876543210 Test Patient Name 01-Jan-2022/subfolder/guid_unknown.pdf",
            "/9876543210 Test Patient Name 01-Jan-2022/subfolder/1of1_Lloyd_George_Record_[Test Patient Name]_[9876543210]_[01-01-2022].pdf",
        ),
        (
            "/9876543210 Test Patient Name 01-jAn-2022/guid_unknown.pdf",
            "/9876543210 Test Patient Name 01-jAn-2022/1of1_Lloyd_George_Record_[Test Patient Name]_[9876543210]_[01-01-2022].pdf",
        ),
        (
            "/9876543210 Test Patient-Name 01-Jan-2022/guid_unknown.pdf",
            "/9876543210 Test Patient-Name 01-Jan-2022/1of1_Lloyd_George_Record_[Test Patient-Name]_[9876543210]_[01-01-2022].pdf",
        ),
        (
            "/9876543210 Test O'Patient 01-Jan-2022/guid_unknown.pdf",
            "/9876543210 Test O'Patient 01-Jan-2022/1of1_Lloyd_George_Record_[Test O'Patient]_[9876543210]_[01-01-2022].pdf",
        ),
        (
            "/9876543210 Test Patient Name 01-01-2022/guid_unknown.pdf",
            "/9876543210 Test Patient Name 01-01-2022/1of1_Lloyd_George_Record_[Test Patient Name]_[9876543210]_[01-01-2022].pdf",
        ),
        (
            "/9876543210Test Patient Name 01-Jan-2022/guid_unknown.pdf",
            "/9876543210Test Patient Name 01-Jan-2022/1of1_Lloyd_George_Record_[Test Patient Name]_[9876543210]_[01-01-2022].pdf",
        ),
        (
            "/9876543210 Test Patient Name01-Jan-2022/guid_unknown.pdf",
            "/9876543210 Test Patient Name01-Jan-2022/1of1_Lloyd_George_Record_[Test Patient Name]_[9876543210]_[01-01-2022].pdf",
        ),
    ],
)
def test_validate_record_filename_valid(test_service, file_path, expected):
    actual = test_service.validate_record_filename(file_path)
    assert actual == expected


@pytest.mark.parametrize(
    "file_path",
    [
        "/9876543210_Test_Patient/guid_unknown.pdf",
        "/123 Test Patient Name 01-Jan-2022/guid_unknown.pdf",
        "/some_other_folder/subfolder/guid_unknown.pdf",
        "/9876543210 Test Patient Name 01-January-2022/guid_unknown.pdf",
        "/9876543210 Test Patient Name 32-Jan-2022/guid_unknown.pdf",
        "/guid_unknown.pdf",
    ],
)
def test_validate_record_filename_invalid(test_service, file_path):
    with pytest.raises(InvalidFileNameException):
        test_service.validate_record_filename(file_path)
