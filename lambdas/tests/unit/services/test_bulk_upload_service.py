import pytest
from services.bulk_upload_service import BulkUploadService
from services.lloyd_george_validator import LGInvalidFilesException
from tests.unit.helpers.data.bulk_upload.expected_data import (
    TEST_SQS_MESSAGE, TEST_STAGING_METADATA)


@pytest.fixture
def mock_uuid(mocker):
    test_uuid = "UUID_MOCK"
    mocker.patch("uuid.uuid4", return_value=test_uuid)
    yield test_uuid


def test_handle_sqs_message_create_record_and_copy_lg_file_when_files_are_valid(
    set_env, mocker, mock_uuid
):
    create_lg_records_and_copy_files = mocker.patch.object(
        BulkUploadService, "create_lg_records_and_copy_files"
    )
    mocker.patch.object(BulkUploadService, "validate_files", return_value=None)

    service = BulkUploadService()
    service.handle_sqs_message(message=TEST_SQS_MESSAGE)

    create_lg_records_and_copy_files.assert_called_with(TEST_STAGING_METADATA)


def test_handle_invalid_message_is_called_when_lg_files_are_invalid(set_env, mocker):
    create_lg_records_and_copy_files = mocker.patch.object(
        BulkUploadService, "create_lg_records_and_copy_files"
    )
    handle_invalid_message = mocker.patch.object(
        BulkUploadService, "handle_invalid_message"
    )
    mocker.patch.object(
        BulkUploadService, "validate_files", side_effect=LGInvalidFilesException
    )

    service = BulkUploadService()
    service.handle_sqs_message(message=TEST_SQS_MESSAGE)

    handle_invalid_message.assert_called()
    create_lg_records_and_copy_files.assert_not_called()
