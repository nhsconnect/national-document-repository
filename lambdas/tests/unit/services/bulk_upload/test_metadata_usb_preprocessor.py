import csv
import os
from io import BytesIO

import pytest
from freezegun import freeze_time

from models.staging_metadata import NHS_NUMBER_FIELD_NAME
from services.bulk_upload.metadata_usb_preprocessor import (
    MetadataUsbPreprocessorService,
)
from tests.unit.conftest import TEST_BASE_DIRECTORY
from utils.exceptions import InvalidFileNameException


@pytest.fixture
def usb_preprocessor_service(set_env, mocker):
    mocker.patch("services.bulk_upload_metadata_preprocessor_service.S3Service")
    service = MetadataUsbPreprocessorService("usb-test")
    return service


@pytest.fixture
def mock_get_metadata_rows_from_file(mocker, usb_preprocessor_service):
    return mocker.patch.object(usb_preprocessor_service, "get_metadata_rows_from_file")


@pytest.fixture
def mock_generate_and_save_csv_file(mocker, usb_preprocessor_service):
    return mocker.patch.object(usb_preprocessor_service, "generate_and_save_csv_file")


@pytest.fixture
def mock_s3_client(mocker, usb_preprocessor_service):
    return mocker.patch.object(usb_preprocessor_service.s3_service, "client")


@pytest.fixture
def mock_metadata_file_get_object():
    def _mock_metadata_file_get_object(test_file_path: str, *args, **kwargs):
        with open(test_file_path, "rb") as file:
            test_file_data = file.read()

        return {"Body": BytesIO(test_file_data)}

    return _mock_metadata_file_get_object


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


def test_generate_renaming_map_with_mixed_file_types(usb_preprocessor_service):
    row1 = {
        "FILEPATH": "9876543210 Test Patient Name 01-01-2022/guid_unknown.pdf",
        "NHS-NO": "1111",
        "SCAN-DATE": "10/10/2010",
        "UPLOAD": "10/10/2010",
    }
    row2 = {
        "FILEPATH": "9876543210 Test Patient Name01-Jan-2022/1 of 1_guid_unknown.tiff",
        "NHS-NO": "1111",
        "SCAN-DATE": "10/10/2010",
        "UPLOAD": "10/10/2010",
    }
    metadata = [row1, row2]
    renaming_map, rejected_rows, rejected_reasons = (
        usb_preprocessor_service.generate_renaming_map(metadata)
    )

    assert len(renaming_map) == 1
    assert len(rejected_rows) == 1
    assert rejected_rows[0] == row2
    assert rejected_reasons[0]["REASON"] == "File extension .tiff is not supported"


def test_generate_renaming_map_with_not_supported_file_types(usb_preprocessor_service):
    row1 = {"FILEPATH": "valid_file2.tiff", "NHS-NO": "1111", "SCAN-DATE": "10/10/2010"}
    row2 = {"FILEPATH": "valid_file.tiff", "NHS-NO": "1111", "SCAN-DATE": "10/10/2010"}
    metadata = [row1, row2]
    renaming_map, rejected_rows, rejected_reasons = (
        usb_preprocessor_service.generate_renaming_map(metadata)
    )

    assert len(renaming_map) == 0
    assert len(rejected_rows) == 2
    assert rejected_rows[1] == row2
    assert rejected_reasons[1]["REASON"] == "File extension .tiff is not supported"


def test_generate_renaming_map_for_usb_format_rejects_rows_with_duplicate_nhs_numbers(
    set_env, usb_preprocessor_service
):

    metadata_rows = [
        {
            "FILEPATH": "9876543210 Test Patient Name 01-01-2022/guid_unknown.pdf",
            NHS_NUMBER_FIELD_NAME: "1111",
            "SCAN-DATE": "10/10/2010",
            "UPLOAD": "10/10/2010",
        },
        {
            "FILEPATH": "file2.pdf",
            NHS_NUMBER_FIELD_NAME: "222",
            "SCAN-DATE": "10/10/2010",
        },
        {
            "FILEPATH": "file3.pdf",
            NHS_NUMBER_FIELD_NAME: "222",
            "SCAN-DATE": "10/10/2010",
        },
        {
            "FILEPATH": "9876543213 Test Patient Name 01-01-2022/guid_unknown.pdf",
            NHS_NUMBER_FIELD_NAME: "3333",
            "SCAN-DATE": "10/10/2010",
            "UPLOAD": "10/10/2010",
        },
    ]

    renaming_map, rejected_rows, rejected_reasons = (
        usb_preprocessor_service.generate_renaming_map(metadata_rows)
    )

    assert rejected_rows == [metadata_rows[1], metadata_rows[2]]

    expected_rejected_reasons = [
        {
            "FILEPATH": "file2.pdf",
            "REASON": "More than one file is found for 222",
        },
        {
            "FILEPATH": "file3.pdf",
            "REASON": "More than one file is found for 222",
        },
    ]
    assert rejected_reasons == expected_rejected_reasons

    expected_renaming_map = [
        (
            metadata_rows[0],
            {
                "FILEPATH": "usb-test/9876543210 Test Patient Name 01-01-2022/"
                "1of1_Lloyd_George_Record_[Test Patient Name]_[9876543210]_[01-01-2022].pdf",
                "SCAN-DATE": "10/10/2010",
                "UPLOAD": "10/10/2010",
                NHS_NUMBER_FIELD_NAME: "1111",
            },
        ),
        (
            metadata_rows[3],
            {
                "FILEPATH": "usb-test/9876543213 Test Patient Name 01-01-2022/"
                "1of1_Lloyd_George_Record_[Test Patient Name]_[9876543213]_[01-01-2022].pdf",
                "SCAN-DATE": "10/10/2010",
                "UPLOAD": "10/10/2010",
                NHS_NUMBER_FIELD_NAME: "3333",
            },
        ),
    ]

    assert renaming_map == expected_renaming_map


@freeze_time("2025-01-01T12:00:00")
def test_process_metadata_file_e2e(
    usb_preprocessor_service,
    mock_s3_client,
    mock_generate_and_save_csv_file,
    mock_metadata_file_get_object,
):
    test_processed_metadata_file = os.path.join(
        TEST_BASE_DIRECTORY,
        "helpers/data/bulk_upload/preprocessed",
        "metadata_usb.csv",
    )

    test_rejections_file = os.path.join(
        TEST_BASE_DIRECTORY,
        "helpers/data/bulk_upload/preprocessed",
        "rejections_usb.csv",
    )

    with open(test_processed_metadata_file, "rb") as file:
        test_file_data = file.read()
    expected_metadata_bytes = test_file_data

    with open(test_rejections_file, "rb") as file:
        test_file_data = file.read()
    expected_rejected_bytes = test_file_data

    test_preprocessed_metadata_file = os.path.join(
        TEST_BASE_DIRECTORY,
        "helpers/data/bulk_upload/preprocessed",
        "preprocessed_metadata_usb.csv",
    )

    mock_s3_client.file_exist_on_s3.return_value = True
    mock_s3_client.get_object.side_effect = (
        lambda Bucket, Key: mock_metadata_file_get_object(
            test_preprocessed_metadata_file, Bucket, Key
        )
    )

    usb_preprocessor_service.process_metadata()

    expected_updated_rows = list(
        csv.DictReader(expected_metadata_bytes.decode("utf-8-sig").splitlines())
    )
    expected_rejected_reasons = list(
        csv.DictReader(expected_rejected_bytes.decode("utf-8-sig").splitlines())
    )

    assert mock_generate_and_save_csv_file.call_count == 2
    assert (
        mock_generate_and_save_csv_file.call_args_list[1][1]["csv_dict"]
        == expected_rejected_reasons
    )
