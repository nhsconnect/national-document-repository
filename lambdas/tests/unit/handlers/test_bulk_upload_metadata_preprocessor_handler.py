import pytest
from handlers.bulk_upload_metadata_preprocessor_handler import lambda_handler
from services.bulk_upload.metadata_general_preprocessor import (
    MetadataGeneralPreprocessor,
)
from services.bulk_upload.metadata_usb_preprocessor import (
    MetadataUsbPreprocessorService,
)


@pytest.fixture
def mock_general_preprocessor(mocker):
    mocked_instance = mocker.patch(
        "handlers.bulk_upload_metadata_preprocessor_handler.MetadataGeneralPreprocessor",
        spec=MetadataGeneralPreprocessor,
    ).return_value
    return mocked_instance


@pytest.fixture
def mock_usb_preprocessor(mocker):
    mocked_instance = mocker.patch(
        "handlers.bulk_upload_metadata_preprocessor_handler.MetadataUsbPreprocessorService",
        spec=MetadataUsbPreprocessorService,
    ).return_value
    return mocked_instance


def test_metadata_preprocessor_lambda_handler_valid_event_no_pre_format_type(
    set_env, context, mock_general_preprocessor, mock_usb_preprocessor
):
    lambda_handler({"practiceDirectory": "test"}, context)

    mock_general_preprocessor.process_metadata.assert_called_once()
    mock_usb_preprocessor.process_metadata.assert_not_called()


def test_metadata_preprocessor_lambda_handler_valid_event_general_pre_format_type(
    set_env, context, mock_general_preprocessor, mock_usb_preprocessor
):
    lambda_handler({"practiceDirectory": "test", "preFormatType": "GENERAL"}, context)

    mock_general_preprocessor.process_metadata.assert_called_once()
    mock_usb_preprocessor.process_metadata.assert_not_called()


def test_metadata_preprocessor_lambda_handler_valid_event_usb_pre_format_type(
    set_env, context, mock_general_preprocessor, mock_usb_preprocessor
):
    lambda_handler({"practiceDirectory": "test", "preFormatType": "USB"}, context)

    mock_usb_preprocessor.process_metadata.assert_not_called()
    mock_general_preprocessor.process_metadata.assert_called_once()


def test_metadata_preprocessor_lambda_handler_valid_event_invalid_pre_format_type(
    set_env, context, mock_general_preprocessor, mock_usb_preprocessor
):
    lambda_handler(
        {"practiceDirectory": "test", "preFormatType": "random_string"}, context
    )

    mock_general_preprocessor.process_metadata.assert_called_once()
    mock_usb_preprocessor.process_metadata.assert_not_called()


def test_metadata_preprocessor_lambda_handler_invalid_event(
    set_env, context, mock_general_preprocessor, mock_usb_preprocessor
):
    lambda_handler({"invalid": "invalid"}, context)

    mock_general_preprocessor.process_metadata.assert_not_called()
    mock_usb_preprocessor.process_metadata.assert_not_called()
