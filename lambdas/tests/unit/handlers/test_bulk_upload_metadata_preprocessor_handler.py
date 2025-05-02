import pytest
from handlers.bulk_upload_metadata_preprocessor_handler import lambda_handler
from services.bulk_upload_metadata_preprocessor_service import (
    MetadataPreprocessorService,
)


def test_lambda_call_process_metadata_of_service_class(
    set_env, event, context, mock_metadata_preprocessing_service
):
    lambda_handler(event, context)

    mock_metadata_preprocessing_service.process_metadata.assert_called_once()


@pytest.fixture
def mock_metadata_preprocessing_service(mocker):
    mocked_instance = mocker.patch(
        "handlers.bulk_upload_metadata_preprocessor_handler.MetadataPreprocessorService",
        spec=MetadataPreprocessorService,
    ).return_value
    yield mocked_instance
