import pytest
from handlers.nems_message_handler import lambda_handler
from services.feature_flags_service import FeatureFlagService
from services.process_nems_message_service import ProcessNemsMessageService
from tests.unit.helpers.data.bulk_upload.test_data import (
    TEST_EVENT_WITH_NO_SQS_MESSAGES,
    TEST_EVENT_WITH_ONE_SQS_MESSAGE,
    TEST_EVENT_WITH_SQS_MESSAGES,
)
from utils.lambda_response import ApiGatewayResponse


@pytest.fixture
def mock_service(mocker):
    yield mocker.patch.object(ProcessNemsMessageService, "process_messages_from_event")


@pytest.fixture
def mock_nems_enabled(mocker):
    mock_function = mocker.patch.object(FeatureFlagService, "get_feature_flags_by_flag")
    mock_nems_feature_flag = mock_function.return_value = {"nemsEnabled": True}
    yield mock_nems_feature_flag


@pytest.fixture
def mock_nems_disabled(mocker):
    mock_function = mocker.patch.object(FeatureFlagService, "get_feature_flags_by_flag")
    mock_nems_feature_flag = mock_function.return_value = {"nemsEnabled": False}
    yield mock_nems_feature_flag


def test_can_process_event_with_one_message_no_error(
    mock_service, context, set_env, mock_nems_enabled
):
    expected = {"batchItemFailures": []}
    mock_service.return_value = []

    actual = lambda_handler(TEST_EVENT_WITH_ONE_SQS_MESSAGE, context)

    assert expected == actual
    mock_service.assert_called_once()


def test_can_process_event_with_several_messages_no_error(
    mock_service, context, set_env, mock_nems_enabled
):
    expected = {"batchItemFailures": []}
    mock_service.return_value = []

    actual = lambda_handler(TEST_EVENT_WITH_SQS_MESSAGES, context)

    assert actual == expected
    mock_service.assert_called_once()


def test_can_process_event_with_several_messages_with_fail(
    mock_service, context, set_env, mock_nems_enabled
):
    expected = {"batchItemFailures": ["test_response"]}
    mock_service.return_value = ["test_response"]

    actual = lambda_handler(TEST_EVENT_WITH_SQS_MESSAGES, context)

    assert actual == expected
    mock_service.assert_called_once()


def test_receive_correct_response_when_no_records_in_event(
    mock_service, context, set_env, mock_nems_enabled
):
    expected = ApiGatewayResponse(
        400,
        "No sqs messages found in event: {'Records': []}. Will ignore this event",
        "GET",
    ).create_api_gateway_response()
    actual = lambda_handler(TEST_EVENT_WITH_NO_SQS_MESSAGES, context)

    assert expected == actual


def test_no_event_processing_when_nems_flag_not_enabled(
    mock_service, context, set_env, mock_nems_disabled
):
    lambda_handler(TEST_EVENT_WITH_SQS_MESSAGES, context)

    mock_service.assert_not_called()
