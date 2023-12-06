import pytest
from botocore.exceptions import ClientError
from handlers.bulk_upload_metadata_handler import lambda_handler
from models.staging_metadata import METADATA_FILENAME
from pydantic import ValidationError
from services.bulk_upload_metadata_service import BulkUploadMetadataService


#
def test_lambda_call_process_metadata_of_service_class(
    set_env, event, context, mock_metadata_service
):
    lambda_handler(event, context)

    mock_metadata_service.process_metadata.assert_called_once_with(METADATA_FILENAME)


def test_handler_handle_client_error(
    set_env, caplog, context, event, mock_metadata_service
):
    mock_client_error = ClientError(
        {"Error": {"Code": "403", "Message": "Forbidden"}},
        "S3:HeadObject",
    )
    mock_metadata_service.process_metadata.side_effect = mock_client_error
    expected_err_msg = 'No metadata file could be found with the name "metadata.csv"'

    lambda_handler(event, context)

    assert caplog.records[-1].msg == expected_err_msg
    assert caplog.records[-1].levelname == "ERROR"


def test_handler_handle_validation_error_when_metadata_csv_is_invalid(
    set_env, caplog, context, event, mock_metadata_service
):
    mock_validation_error = ValidationError.from_exception_data(
        "mock validation error", []
    )
    mock_metadata_service.process_metadata.side_effect = mock_validation_error

    lambda_handler(event, context)

    assert "validation error" in caplog.records[-1].msg
    assert caplog.records[-1].levelname == "ERROR"


@pytest.fixture
def mock_metadata_service(mocker):
    mocked_instance = mocker.patch(
        "handlers.bulk_upload_metadata_handler.BulkUploadMetadataService",
        spec=BulkUploadMetadataService,
    ).return_value
    yield mocked_instance
