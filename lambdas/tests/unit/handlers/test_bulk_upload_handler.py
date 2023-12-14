import pytest
from handlers.bulk_upload_handler import lambda_handler
from services.bulk_upload_service import BulkUploadService
from tests.unit.helpers.data.bulk_upload.test_data import (
    TEST_EVENT_WITH_NO_SQS_MESSAGES,
    TEST_EVENT_WITH_ONE_SQS_MESSAGE,
    TEST_EVENT_WITH_SQS_MESSAGES,
)
from utils.exceptions import BulkUploadException
from utils.lambda_response import ApiGatewayResponse


@pytest.fixture
def mock_service(mocker):
    yield mocker.patch.object(BulkUploadService, "process_message_queue")


def test_can_process_event_with_one_message(mock_service, context, set_env):
    expected = ApiGatewayResponse(
        200, "Finished processing all 1 messages", "GET"
    ).create_api_gateway_response()
    actual = lambda_handler(TEST_EVENT_WITH_ONE_SQS_MESSAGE, context)

    assert expected == actual


def test_can_process_event_with_several_messages(mock_service, context, set_env):
    expected = ApiGatewayResponse(
        200, "Finished processing all 3 messages", "GET"
    ).create_api_gateway_response()
    actual = lambda_handler(TEST_EVENT_WITH_SQS_MESSAGES, context)

    assert actual == expected


def test_receive_correct_response_when_service_returns_error(
    mock_service, context, set_env
):
    expected = ApiGatewayResponse(
        500, "Bulk upload failed with error: ", "GET"
    ).create_api_gateway_response()
    mock_service.side_effect = BulkUploadException()
    actual = lambda_handler(TEST_EVENT_WITH_SQS_MESSAGES, context)

    assert actual == expected


def test_receive_correct_response_when_no_records_in_event(
    mock_service, context, set_env
):
    expected = ApiGatewayResponse(
        400,
        "No sqs messages found in event: {'Records': []}. Will ignore this event",
        "GET",
    ).create_api_gateway_response()
    actual = lambda_handler(TEST_EVENT_WITH_NO_SQS_MESSAGES, context)

    assert expected == actual
