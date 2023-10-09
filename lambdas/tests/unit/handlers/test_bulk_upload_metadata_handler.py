import tempfile

import pytest
from botocore.exceptions import ClientError
from handlers.bulk_upload_metadata_handler import (csv_to_staging_metadata,
                                                   download_metadata_from_s3,
                                                   lambda_handler,
                                                   send_metadata_to_sqs)
from models.staging_metadata import METADATA_FILENAME
from tests.unit.conftest import (MOCK_LG_METADATA_SQS_QUEUE,
                                 MOCK_LG_STAGING_STORE_BUCKET)
from tests.unit.helpers.data.staging_metadata.expected_data import (
    EXPECTED_PARSED_METADATA, EXPECTED_SQS_MSG_FOR_PATIENT_1234567890,
    EXPECTED_SQS_MSG_FOR_PATIENT_1234567891)

MOCK_METADATA_CSV = "tests/unit/helpers/data/staging_metadata/metadata.csv"
MOCK_INVALID_METADATA_CSV = (
    "tests/unit/helpers/data/staging_metadata/metadata_invalid.csv"
)
MOCK_TEMP_FOLDER = "tests/unit/helpers/data/staging_metadata"


def test_lambda_send_metadata_to_sqs_queue(set_env, mocker, mock_sqs_service):
    mocker.patch(
        "handlers.bulk_upload_metadata_handler.download_metadata_from_s3",
        return_value=MOCK_METADATA_CSV,
    )

    lambda_handler(None, None)

    assert mock_sqs_service.send_message_with_nhs_number_attr.call_count == 2

    mock_sqs_service.send_message_with_nhs_number_attr.assert_any_call(
        queue_url=MOCK_LG_METADATA_SQS_QUEUE,
        message_body=EXPECTED_SQS_MSG_FOR_PATIENT_1234567890,
        nhs_number="1234567890",
    )

    mock_sqs_service.send_message_with_nhs_number_attr.assert_any_call(
        queue_url=MOCK_LG_METADATA_SQS_QUEUE,
        message_body=EXPECTED_SQS_MSG_FOR_PATIENT_1234567891,
        nhs_number="1234567891",
    )


def test_handler_log_error_when_fail_to_get_metadata_csv_from_s3(
    set_env, mock_s3_service, mock_sqs_service, caplog
):
    mock_s3_service.download_file.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "file not exist in bucket"}},
        "s3_get_object",
    )
    expected_err_msg = "An error occurred (500) when calling the s3_get_object operation: file not exist in bucket"

    lambda_handler(None, None)

    assert caplog.records[-1].message == expected_err_msg
    assert caplog.records[-1].levelname == "ERROR"

    mock_sqs_service.send_message_with_nhs_number_attr.assert_not_called()


def test_handler_log_error_when_metadata_csv_is_invalid(
    set_env, mocker, mock_sqs_service, caplog
):
    mocker.patch(
        "handlers.bulk_upload_metadata_handler.download_metadata_from_s3",
        return_value=MOCK_INVALID_METADATA_CSV,
    )

    lambda_handler(None, None)

    assert "validation errors for MetadataFile" in caplog.records[-1].message
    assert caplog.records[-1].levelname == "ERROR"

    mock_sqs_service.send_message_with_nhs_number_attr.assert_not_called()


def test_handler_log_error_when_failed_to_send_message_to_sqs(
    set_env, mock_s3_service, mock_sqs_service, mock_tempfile, caplog
):
    mock_sqs_service.send_message_with_nhs_number_attr.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "Queue not exist"}},
        "sqs_send_message",
    )
    expected_err_msg = "An error occurred (500) when calling the sqs_send_message operation: Queue not exist"

    lambda_handler(None, None)

    assert caplog.records[-1].message == expected_err_msg
    assert caplog.records[-1].levelname == "ERROR"


def test_download_metadata_from_s3(mock_s3_service, mock_tempfile):
    actual = download_metadata_from_s3(
        staging_bucket_name=MOCK_LG_STAGING_STORE_BUCKET,
        metadata_filename=METADATA_FILENAME,
    )
    expected = MOCK_METADATA_CSV

    mock_s3_service.download_file.assert_called_with(
        s3_bucket_name=MOCK_LG_STAGING_STORE_BUCKET,
        file_key=METADATA_FILENAME,
        download_path=f"{MOCK_TEMP_FOLDER}/{METADATA_FILENAME}",
    )
    assert actual == expected


def test_csv_to_staging_metadata():
    actual = csv_to_staging_metadata(MOCK_METADATA_CSV)
    expected = EXPECTED_PARSED_METADATA
    assert actual == expected


def test_send_metadata_to_sqs(mock_sqs_service, mocker):
    mock_parsed_metadata = EXPECTED_PARSED_METADATA
    send_metadata_to_sqs(mock_parsed_metadata, MOCK_LG_METADATA_SQS_QUEUE)

    assert mock_sqs_service.send_message_with_nhs_number_attr.call_count == 2

    mock_sqs_service.send_message_with_nhs_number_attr.assert_any_call(
        queue_url=MOCK_LG_METADATA_SQS_QUEUE,
        message_body=EXPECTED_SQS_MSG_FOR_PATIENT_1234567890,
        nhs_number="1234567890",
    )

    mock_sqs_service.send_message_with_nhs_number_attr.assert_any_call(
        queue_url=MOCK_LG_METADATA_SQS_QUEUE,
        message_body=EXPECTED_SQS_MSG_FOR_PATIENT_1234567891,
        nhs_number="1234567891",
    )


@pytest.fixture
def mock_s3_service(mocker):
    patched_instance = mocker.patch(
        "handlers.bulk_upload_metadata_handler.S3Service"
    ).return_value
    yield patched_instance


@pytest.fixture
def mock_tempfile(mocker):
    mocker.patch.object(tempfile, "mkdtemp", return_value=MOCK_TEMP_FOLDER)
    yield


@pytest.fixture
def mock_sqs_service(mocker):
    patched_instance = mocker.patch(
        "handlers.bulk_upload_metadata_handler.SQSService"
    ).return_value
    yield patched_instance
