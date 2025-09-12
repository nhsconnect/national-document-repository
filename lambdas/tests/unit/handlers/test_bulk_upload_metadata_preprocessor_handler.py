import pytest
from handlers.bulk_upload_metadata_preprocessor_handler import lambda_handler
from services.bulk_upload_metadata_preprocessor_service import (
    MetadataPreprocessorService,
)


@pytest.fixture
def mock_metadata_preprocessing_service(mocker):
    mocked_instance = mocker.patch(
        "handlers.bulk_upload_metadata_preprocessor_handler.MetadataGeneralPreprocessor",
        spec=MetadataPreprocessorService,
    ).return_value
    return mocked_instance


def test_metadata_preprocessor_lambda_handler_valid_event(
    set_env, context, mock_metadata_preprocessing_service
):
    lambda_handler({"practiceDirectory": "test"}, context)

    mock_metadata_preprocessing_service.process_metadata.assert_called_once()


def test_metadata_preprocessor_lambda_handler_invalid_event(
    set_env, context, mock_metadata_preprocessing_service
):
    lambda_handler({"invalid": "invalid"}, context)

    mock_metadata_preprocessing_service.process_metadata.assert_not_called()
