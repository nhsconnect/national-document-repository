import csv
import datetime
import os
from io import BytesIO
from unittest.mock import call

import pytest
from freezegun import freeze_time
from models.staging_metadata import METADATA_FILENAME
from services.bulk_upload.metadata_general_preprocessor import (
    MetadataGeneralPreprocessor,
)
from tests.unit.conftest import TEST_BASE_DIRECTORY
from utils.exceptions import InvalidFileNameException


@pytest.fixture(autouse=True)
@freeze_time("2025-01-01T12:00:00")
def test_service(mocker, set_env):
    service = MetadataGeneralPreprocessor(practice_directory="test_practice_directory")
    return service


@pytest.fixture
def mock_s3_service(mocker, test_service):
    return mocker.patch.object(test_service, "s3_service")


@pytest.fixture
def mock_generate_and_save_csv_file(mocker, test_service):
    return mocker.patch.object(test_service, "generate_and_save_csv_file")


@pytest.fixture
def mock_metadata_file_get_object():
    def _mock_metadata_file_get_object(test_file_path: str, *args, **kwargs):
        with open(test_file_path, "rb") as file:
            test_file_data = file.read()

        return {"Body": BytesIO(test_file_data)}

    return _mock_metadata_file_get_object


@pytest.mark.parametrize(
    "original_filename, mock_details, expected_result",
    [
        (
            "/M89002/01 of 02_Lloyd_George_Record_[Dwayne The Rock Johnson]_[9730787506]_[18-09-1974].pdf",
            {
                "extract_document_path_for_lloyd_george_record": {
                    "args": (
                        "/M89002/01 of 02_Lloyd_George_Record_[Dwayne The Rock Johnson]_[9730787506]_[18-09-1974].pdf",
                    ),
                    "return_value": (
                        "/M89002/",
                        "01 of 02_Lloyd_George_Record_[Dwayne The Rock Johnson]_[9730787506]_[18-09-1974].pdf",
                    ),
                },
                "extract_document_number_bulk_upload_file_name": {
                    "args": (
                        "01 of 02_Lloyd_George_Record_[Dwayne The Rock Johnson]_[9730787506]_[18-09-1974].pdf",
                    ),
                    "return_value": (
                        "01",
                        "02",
                        "_Lloyd_George_Record_[Dwayne The Rock Johnson]_[9730787506]_[18-09-1974].pdf",
                    ),
                },
                "extract_lloyd_george_record_from_bulk_upload_file_name": {
                    "args": (
                        "_Lloyd_George_Record_[Dwayne The Rock Johnson]_[9730787506]_[18-09-1974].pdf",
                    ),
                    "return_value": "_[Dwayne The Rock Johnson]_[9730787506]_[18-09-1974].pdf",
                },
                "extract_patient_name_from_bulk_upload_file_name": {
                    "args": (
                        "_[Dwayne The Rock Johnson]_[9730787506]_[18-09-1974].pdf",
                    ),
                    "return_value": (
                        "Dwayne The Rock Johnson",
                        "_[9730787506]_[18-09-1974].pdf",
                    ),
                },
                "extract_nhs_number_from_bulk_upload_file_name": {
                    "args": ("_[9730787506]_[18-09-1974].pdf",),
                    "return_value": ("9730787506", "_[18-09-1974].pdf"),
                },
                "extract_date_from_bulk_upload_file_name": {
                    "args": ("_[18-09-1974].pdf",),
                    "return_value": (datetime.date(1974, 9, 18), ".pdf"),
                },
                "extract_file_extension_from_bulk_upload_file_name": {
                    "args": (".pdf",),
                    "return_value": "pdf",
                },
                "assemble_lg_valid_file_name_full_path": {
                    "args": (
                        "/M89002/",
                        "01",
                        "02",
                        "Dwayne The Rock Johnson",
                        "9730787506",
                        datetime.date(1974, 9, 18),
                        "pdf",
                    ),
                    "return_value": "final_filename.pdf",
                },
            },
            "final_filename.pdf",
        )
    ],
)
def test_validate_record_filename_valid(
    test_service, mocker, original_filename, mock_details, expected_result
):
    mocks = {}
    for function_name, details in mock_details.items():
        mocks[function_name] = mocker.patch(
            f"services.bulk_upload.metadata_general_preprocessor.{function_name}",
            return_value=details["return_value"],
        )

    result = test_service.validate_record_filename(original_filename)

    assert result == expected_result

    for function_name, details in mock_details.items():
        mocks[function_name].assert_called_once_with(*details["args"])


@pytest.mark.parametrize(
    "original_filename, mock_details, expected_exception_message",
    [
        (
            "01 of 02_Lloyd_George_Record_[John Doe]_[12345]_[01-01-2000].pdf",
            {
                "extract_document_path_for_lloyd_george_record": {
                    "args": (
                        "01 of 02_Lloyd_George_Record_[John Doe]_[12345]_[01-01-2000].pdf",
                    ),
                    "return_value": (
                        "prefix/",
                        "01 of 02_Lloyd_George_Record_[John Doe]_[12345]_[01-01-2000].pdf",
                    ),
                },
                "extract_document_number_bulk_upload_file_name": {
                    "args": (
                        "01 of 02_Lloyd_George_Record_[John Doe]_[12345]_[01-01-2000].pdf",
                    ),
                    "return_value": (
                        "01",
                        "02",
                        "_Lloyd_George_Record_[John Doe]_[12345]_[01-01-2000].pdf",
                    ),
                },
                "extract_lloyd_george_record_from_bulk_upload_file_name": {
                    "args": (
                        "_Lloyd_George_Record_[John Doe]_[12345]_[01-01-2000].pdf",
                    ),
                    "return_value": "_[John Doe]_[12345]_[01-01-2000].pdf",
                },
                "extract_patient_name_from_bulk_upload_file_name": {
                    "args": ("_[John Doe]_[12345]_[01-01-2000].pdf",),
                    "side_effect": InvalidFileNameException(
                        "Incorrect NHS number or date format"
                    ),
                },
                "extract_nhs_number_from_bulk_upload_file_name": {},
            },
            "Incorrect NHS number or date format",
        )
    ],
)
def test_validate_record_filename_invalid(
    mocker, test_service, original_filename, mock_details, expected_exception_message
):
    mocks = {}
    for function_name, details in mock_details.items():
        mocks[function_name] = mocker.patch(
            f"services.bulk_upload.metadata_general_preprocessor.{function_name}",
            **{
                k: v for k, v in details.items() if k in ["return_value", "side_effect"]
            },
        )

    with pytest.raises(InvalidFileNameException) as exc_info:
        test_service.validate_record_filename(original_filename)

    assert str(exc_info.value) == expected_exception_message

    for function_name, details in mock_details.items():
        if details:
            mocks[function_name].assert_called_once_with(*details["args"])
        else:
            mocks[function_name].assert_not_called()


def test_validate_record_filename_invalid_digit_count(mocker, test_service, caplog):
    bad_filename = "01 of 02_Lloyd_George_Record_[John Doe]_[12345]_[01-01-2000].pdf"

    mocker.patch(
        "services.bulk_upload.metadata_general_preprocessor.extract_document_path_for_lloyd_george_record",
        return_value=("prefix", bad_filename),
    )
    mocker.patch(
        "services.bulk_upload.metadata_general_preprocessor.extract_document_number_bulk_upload_file_name",
        return_value=("01", "02", bad_filename),
    )
    mocker.patch(
        "services.bulk_upload.metadata_general_preprocessor.extract_lloyd_george_record_from_bulk_upload_file_name",
        return_value=("LG", bad_filename),
    )
    mocker.patch(
        "services.bulk_upload.metadata_general_preprocessor.extract_patient_name_from_bulk_upload_file_name",
        return_value=("John Doe", bad_filename),
    )

    with pytest.raises(InvalidFileNameException) as exc_info:
        test_service.validate_record_filename(bad_filename)

    assert str(exc_info.value) == "Incorrect NHS number or date format"


@freeze_time("2025-01-01T12:00:00")
def test_process_metadata_file_exists(
    test_service,
    mock_metadata_file_get_object,
    mock_generate_and_save_csv_file,
    mock_s3_service,
):
    test_processed_metadata_file = os.path.join(
        TEST_BASE_DIRECTORY,
        "helpers/data/bulk_upload/preprocessed",
        f"{METADATA_FILENAME}",
    )

    test_rejections_file = os.path.join(
        TEST_BASE_DIRECTORY,
        "helpers/data/bulk_upload/preprocessed",
        "rejected.csv",
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
        f"preprocessed_{METADATA_FILENAME}",
    )

    mock_s3_service.file_exist_on_s3.return_value = True
    mock_s3_service.client.get_object.side_effect = (
        lambda Bucket, Key: mock_metadata_file_get_object(
            test_preprocessed_metadata_file, Bucket, Key
        )
    )

    test_service.process_metadata()

    expected_updated_rows = list(
        csv.DictReader(expected_metadata_bytes.decode("utf-8-sig").splitlines())
    )
    expected_rejected_reasons = list(
        csv.DictReader(expected_rejected_bytes.decode("utf-8-sig").splitlines())
    )

    expected_calls = [
        call(
            csv_dict=expected_updated_rows,
            file_key=f"test_practice_directory/{METADATA_FILENAME}",
        ),
        call(
            csv_dict=expected_rejected_reasons,
            file_key="test_practice_directory/processed/2025-01-01 12:00/rejections.csv",
        ),
    ]

    mock_generate_and_save_csv_file.assert_has_calls(expected_calls, any_order=True)
