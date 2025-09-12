import pytest
from handlers.V2_bulk_upload_metadata_handler import lambda_handler
from services.V2_bulk_upload_metadata_service import V2BulkUploadMetadataService


@pytest.fixture
def mock_metadata_service(mocker):
    mocked_instance = mocker.patch(
        "handlers.V2_bulk_upload_metadata_handler.V2BulkUploadMetadataService",
        spec=V2BulkUploadMetadataService,
    ).return_value
    return mocked_instance


def test_metadata_preprocessor_lambda_handler_valid_event(
    set_env, context, mock_metadata_service
):
    lambda_handler({"practiceDirectory": "test"}, context)

    mock_metadata_service.process_metadata.assert_called_once()


def test_metadata_preprocessor_lambda_handler_invalid_event(
    set_env, context, mock_metadata_service
):
    lambda_handler({"invalid": "invalid"}, context)

    mock_metadata_service.process_metadata.assert_not_called()
