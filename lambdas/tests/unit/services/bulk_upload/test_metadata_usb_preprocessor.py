import pytest
from services.bulk_upload.metadata_usb_preprocessor import (
    MetadataUsbPreprocessorService,
)
from utils.exceptions import InvalidFileNameException


@pytest.fixture
def usb_preprocessor_service(set_env):
    service = MetadataUsbPreprocessorService()
    return service


@pytest.mark.parametrize(
    "file_path, expected",
    [
        (
            "/9876543210 Test Patient Name 01-Jan-2022/guid_unknown.pdf",
            "/9876543210 Test Patient Name 01-Jan-2022/1of1_Lloyd_George_Record_[Test Patient Name]_[9876543210]_"
            "[01-01-2022].pdf",
        ),
        (
            "/1234567890 Test Patient With A Very Long Name 01-Jan-2022/guid_unknown.pdf",
            "/1234567890 Test Patient With A Very Long Name 01-Jan-2022/1of1_Lloyd_George_Record_[Test Patient With A "
            "Very Long Name]_[1234567890]_[01-01-2022].pdf",
        ),
        (
            "/9876543210 Test Patient Name 01-Jan-2022/subfolder/guid_unknown.pdf",
            "/9876543210 Test Patient Name 01-Jan-2022/subfolder/1of1_Lloyd_George_Record_[Test Patient Name]_[9876543210]"
            "_[01-01-2022].pdf",
        ),
        (
            "/9876543210 Test Patient Name 01-jAn-2022/guid_unknown.pdf",
            "/9876543210 Test Patient Name 01-jAn-2022/1of1_Lloyd_George_Record_[Test Patient Name]_[9876543210]_"
            "[01-01-2022].pdf",
        ),
        (
            "/9876543210 Test Patient-Name 01-Jan-2022/guid_unknown.pdf",
            "/9876543210 Test Patient-Name 01-Jan-2022/1of1_Lloyd_George_Record_[Test Patient-Name]_[9876543210]_"
            "[01-01-2022].pdf",
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
            "/9876543210 Test Patient_01-Jan-2022/guid_unknown.pdf",
            "/9876543210 Test Patient_01-Jan-2022/1of1_Lloyd_George_Record_[Test Patient]_[9876543210]_[01-01-2022].pdf",
        ),
        (
            "/9876543210 Test Patient-01-Jan-2022/1 of 1_guid_unknown.pdf",
            "/9876543210 Test Patient-01-Jan-2022/1of1_Lloyd_George_Record_[Test Patient]_[9876543210]_[01-01-2022].pdf",
        ),
    ],
)
def test_validate_record_filename_formats_valid_paths(
    usb_preprocessor_service, file_path, expected
):
    actual = usb_preprocessor_service.validate_record_filename(file_path)
    assert actual == expected


@pytest.mark.parametrize(
    "file_path",
    [
        "/9876543210_Test_Patient/guid_unknown.pdf",
        "/123 Test Patient Name 01-Jan-2022/guid_unknown.pdf",
        "/some_other_folder/subfolder/guid_unknown.pdf",
        "/9876543210 Test Patient Name 01-January-2022/guid_unknown.pdf",
        "/9876543210 Test Patient Name 32-Jan-2022/guid_unknown.pdf",
        "/9876543210 Test Patient Name 32-Jan-2022/1of3guid_unknown.pdf",
        "/9876543210 Test Patient Name 01-01-2022-23-59-59/1 of 02_Lloyd_George_Record",
        "/9876543210 Test Patient Name 01-01-2022-23-59-59/3 of 2_Lloyd_George_Record",
        "/guid_unknown.pdf",
        "/9876543210 Test Patient Name01-Jan-2022/1 of 1_guid_unknown.tiff",
    ],
)
def test_validate_record_filename_raises_for_invalid_paths(
    usb_preprocessor_service, file_path
):
    with pytest.raises(InvalidFileNameException):
        usb_preprocessor_service.validate_record_filename(file_path)
