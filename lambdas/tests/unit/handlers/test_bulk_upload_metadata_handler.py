import pytest
from handlers.bulk_upload_metadata_handler import lambda_handler
from models.staging_metadata import METADATA_FILENAME
from services.bulk_upload_metadata_service import BulkUploadMetadataService


def test_lambda_call_process_metadata_of_service_class(
    set_env, event, context, mock_metadata_service
):
    lambda_handler(event, context)

    mock_metadata_service.process_metadata.assert_called_once_with(METADATA_FILENAME)


@pytest.fixture
def mock_metadata_service(mocker):
    mocked_instance = mocker.patch(
        "handlers.bulk_upload_metadata_handler.BulkUploadMetadataService",
        spec=BulkUploadMetadataService,
    ).return_value
    yield mocked_instance
