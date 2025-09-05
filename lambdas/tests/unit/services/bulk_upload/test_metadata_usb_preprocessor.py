import pytest

from services.bulk_upload.metadata_usb_preprocessor import (
    MetadataUsbPreprocessorService,
)
from utils.exceptions import InvalidFileNameException


class TestMetadataUsbPreprocessorService:
    def setup_method(self):
        self.service = MetadataUsbPreprocessorService()

    def test_validate_record_filename_valid(self):
        file_path = "/9876543210 Test Patient Name 01-Jan-2022/guid_unknown.pdf"
        expected = "/9876543210 Test Patient Name 01-Jan-2022/1of1_Lloyd_George_Record_[Test Patient Name]_[9876543210]_[01-01-2022].pdf"
        actual = self.service.validate_record_filename(file_path)
        assert actual == expected

    def test_validate_record_filename_invalid_directory_format(self):
        file_path = "/9876543210_Test_Patient/guid_unknown.pdf"
        with pytest.raises(InvalidFileNameException):
            self.service.validate_record_filename(file_path)

    def test_validate_record_filename_invalid_nhs_number(self):
        file_path = "/123 Test Patient Name 01-Jan-2022/guid_unknown.pdf"
        with pytest.raises(InvalidFileNameException):
            self.service.validate_record_filename(file_path)

    def test_validate_record_filename_long_patient_name(self):
        file_path = (
            "/1234567890 Test Patient With A Very Long Name 01-Jan-2022/guid_unknown.pdf"
        )
        expected = "/1234567890 Test Patient With A Very Long Name 01-Jan-2022/1of1_Lloyd_George_Record_[Test Patient With A Very Long Name]_[1234567890]_[01-01-2022].pdf"
        actual = self.service.validate_record_filename(file_path)
        assert actual == expected

    def test_validate_record_filename_nested_file(self):
        file_path = (
            "/9876543210 Test Patient Name 01-Jan-2022/subfolder/guid_unknown.pdf"
        )
        expected = "/9876543210 Test Patient Name 01-Jan-2022/subfolder/1of1_Lloyd_George_Record_[Test Patient Name]_[9876543210]_[01-01-2022].pdf"
        actual = self.service.validate_record_filename(file_path)
        assert actual == expected

    def test_validate_record_filename_no_valid_parent_dir(self):
        file_path = "/some_other_folder/subfolder/guid_unknown.pdf"
        with pytest.raises(InvalidFileNameException):
            self.service.validate_record_filename(file_path)
