import tempfile
from unittest.mock import call

import pytest
from botocore.exceptions import ClientError
from models.staging_metadata import METADATA_FILENAME
from pydantic import ValidationError
from services.bulk_upload_metadata_service import BulkUploadMetadataService
from tests.unit.conftest import (MOCK_LG_METADATA_SQS_QUEUE,
                                 MOCK_LG_STAGING_STORE_BUCKET)
from tests.unit.helpers.data.bulk_upload.test_data import (
    EXPECTED_PARSED_METADATA, EXPECTED_SQS_MSG_FOR_PATIENT_1234567890,
    EXPECTED_SQS_MSG_FOR_PATIENT_1234567891)

MOCK_METADATA_CSV = "tests/unit/helpers/data/bulk_upload/metadata.csv"
MOCK_INVALID_METADATA_CSV_FILES = [
    "tests/unit/helpers/data/bulk_upload/metadata_invalid.csv",
    "tests/unit/helpers/data/bulk_upload/metadata_invalid_empty_nhs_number.csv",
    "tests/unit/helpers/data/bulk_upload/metadata_invalid_unexpected_comma.csv",
]
MOCK_TEMP_FOLDER = "tests/unit/helpers/data/bulk_upload"


def test_process_metadata_send_metadata_to_sqs_queue(
    set_env, mocker, metadata_filename, mock_sqs_service, mock_download_metadata_from_s3
):
    mock_download_metadata_from_s3.return_value = MOCK_METADATA_CSV
    mocker.patch("uuid.uuid4", return_value="123412342")
    expected_calls = [
        call(
            group_id="bulk_upload_123412342",
            queue_url=MOCK_LG_METADATA_SQS_QUEUE,
            message_body=EXPECTED_SQS_MSG_FOR_PATIENT_1234567890,
            nhs_number="1234567890",
        ),
        call(
            group_id="bulk_upload_123412342",
            queue_url=MOCK_LG_METADATA_SQS_QUEUE,
            message_body=EXPECTED_SQS_MSG_FOR_PATIENT_1234567891,
            nhs_number="1234567891",
        ),
    ]

    service = BulkUploadMetadataService()
    service.process_metadata(metadata_filename)

    assert mock_sqs_service.send_message_with_nhs_number_attr_fifo.call_count == 2
    mock_sqs_service.send_message_with_nhs_number_attr_fifo.assert_has_calls(
        expected_calls
    )


def test_process_metadata_propagate_client_error_when_fail_to_get_metadata_csv_from_s3(
    set_env, metadata_filename, mock_s3_service, mock_sqs_service
):
    mock_s3_service.download_file.side_effect = ClientError(
        {"Error": {"Code": "403", "Message": "Forbidden"}},
        "S3:HeadObject",
    )
    expected_err_msg = (
        "An error occurred (403) when calling the S3:HeadObject operation: Forbidden"
    )

    service = BulkUploadMetadataService()
    with pytest.raises(ClientError) as e:
        service.process_metadata(metadata_filename)

    assert str(e.value) == expected_err_msg
    mock_sqs_service.send_message_with_nhs_number_attr_fifo.assert_not_called()


def test_process_metadata_raise_validation_error_when_metadata_csv_is_invalid(
    set_env, metadata_filename, mock_sqs_service, mock_download_metadata_from_s3
):
    service = BulkUploadMetadataService()

    for invalid_csv_file in MOCK_INVALID_METADATA_CSV_FILES:
        mock_download_metadata_from_s3.return_value = invalid_csv_file

        with pytest.raises(ValidationError):
            service.process_metadata(metadata_filename)

        mock_sqs_service.send_message_with_nhs_number_attr_fifo.assert_not_called()


def test_process_metadata_raise_client_error_when_failed_to_send_message_to_sqs(
    set_env, metadata_filename, mock_s3_service, mock_sqs_service, mock_tempfile
):
    mock_client_error = ClientError(
        {
            "Error": {
                "Code": "AWS.SimpleQueueService.NonExistentQueue",
                "Message": "The specified queue does not exist",
            }
        },
        "SendMessage",
    )
    mock_sqs_service.send_message_with_nhs_number_attr_fifo.side_effect = (
        mock_client_error
    )
    expected_err_msg = (
        "An error occurred (AWS.SimpleQueueService.NonExistentQueue) when calling the SendMessage operation:"
        " The specified queue does not exist"
    )

    service = BulkUploadMetadataService()
    with pytest.raises(ClientError) as e:
        service.process_metadata(metadata_filename)

    assert str(e.value) == expected_err_msg


def test_download_metadata_from_s3(
    set_env, metadata_filename, mock_s3_service, mock_tempfile
):
    service = BulkUploadMetadataService()
    actual = service.download_metadata_from_s3(metadata_filename)
    expected = MOCK_METADATA_CSV

    mock_s3_service.download_file.assert_called_with(
        s3_bucket_name=MOCK_LG_STAGING_STORE_BUCKET,
        file_key=metadata_filename,
        download_path=f"{MOCK_TEMP_FOLDER}/{metadata_filename}",
    )
    assert actual == expected


def test_download_metadata_from_s3_raise_error_when_failed_to_download(
    set_env, metadata_filename, mock_s3_service, mock_tempfile
):
    service = BulkUploadMetadataService()
    mock_s3_service.download_file.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "file not exist in bucket"}},
        "s3_get_object",
    )

    with pytest.raises(ClientError):
        service.download_metadata_from_s3(metadata_filename)


def test_csv_to_staging_metadata(set_env):
    service = BulkUploadMetadataService()
    actual = service.csv_to_staging_metadata(MOCK_METADATA_CSV)
    expected = EXPECTED_PARSED_METADATA
    assert actual == expected


def test_csv_to_staging_metadata_raise_error_when_metadata_invalid(set_env):
    service = BulkUploadMetadataService()
    for invalid_csv_file in MOCK_INVALID_METADATA_CSV_FILES:
        with pytest.raises(ValidationError):
            service.csv_to_staging_metadata(invalid_csv_file)


def test_send_metadata_to_sqs(set_env, mocker, mock_sqs_service):
    service = BulkUploadMetadataService()
    mock_parsed_metadata = EXPECTED_PARSED_METADATA
    mocker.patch("uuid.uuid4", return_value="123412342")
    expected_calls = [
        call(
            queue_url=MOCK_LG_METADATA_SQS_QUEUE,
            message_body=EXPECTED_SQS_MSG_FOR_PATIENT_1234567890,
            nhs_number="1234567890",
            group_id="bulk_upload_123412342",
        ),
        call(
            queue_url=MOCK_LG_METADATA_SQS_QUEUE,
            message_body=EXPECTED_SQS_MSG_FOR_PATIENT_1234567891,
            nhs_number="1234567891",
            group_id="bulk_upload_123412342",
        ),
    ]

    service.send_metadata_to_fifo_sqs(mock_parsed_metadata)

    mock_sqs_service.send_message_with_nhs_number_attr_fifo.assert_has_calls(
        expected_calls
    )
    assert mock_sqs_service.send_message_with_nhs_number_attr_fifo.call_count == 2


def test_send_metadata_to_sqs_raise_error_when_fail_to_send_message(
    set_env, mock_sqs_service
):
    service = BulkUploadMetadataService()
    mock_sqs_service.send_message_with_nhs_number_attr_fifo.side_effect = ClientError(
        {
            "Error": {
                "Code": "AWS.SimpleQueueService.NonExistentQueue",
                "Message": "The specified queue does not exist",
            }
        },
        "SendMessage",
    )

    with pytest.raises(ClientError):
        service.send_metadata_to_fifo_sqs(EXPECTED_PARSED_METADATA)


def test_clear_temp_storage(set_env, mocker, mock_tempfile):
    mocked_rm = mocker.patch("shutil.rmtree")
    service = BulkUploadMetadataService()

    service.clear_temp_storage()

    mocked_rm.assert_called_once_with(service.temp_download_dir)


@pytest.fixture
def metadata_filename():
    return METADATA_FILENAME


@pytest.fixture
def mock_download_metadata_from_s3(mocker):
    yield mocker.patch.object(BulkUploadMetadataService, "download_metadata_from_s3")


@pytest.fixture
def mock_s3_service(mocker):
    patched_instance = mocker.patch(
        "services.bulk_upload_metadata_service.S3Service"
    ).return_value
    yield patched_instance


@pytest.fixture
def mock_tempfile(mocker):
    mocker.patch.object(tempfile, "mkdtemp", return_value=MOCK_TEMP_FOLDER)
    mocker.patch("shutil.rmtree")
    yield


@pytest.fixture
def mock_sqs_service(mocker):
    patched_instance = mocker.patch(
        "services.bulk_upload_metadata_service.SQSService"
    ).return_value
    yield patched_instance
