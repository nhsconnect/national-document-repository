import json

import pytest
from handlers.send_feedback_handler import lambda_handler
from tests.unit.helpers.data.feedback.mock_data import MOCK_VALID_SEND_FEEDBACK_EVENT
from utils.lambda_response import ApiGatewayResponse


def test_lambda_handler_respond_200_with_valid_input(
    set_env, context, mock_feedback_service
):
    test_event = MOCK_VALID_SEND_FEEDBACK_EVENT

    expected = ApiGatewayResponse(
        status_code=200, body="Feedback email processed", methods="POST"
    ).create_api_gateway_response()

    actual = lambda_handler(test_event, context)

    assert actual == expected


def test_lambda_handler_respond_with_400_when_no_event_body_given(set_env, context):
    test_event = {"key1": "value1", "httpMethod": "POST"}
    expected = ApiGatewayResponse(
        status_code=400,
        body=json.dumps(
            {"message": "Missing POST request body", "err_code": "SFB_4001"}
        ),
        methods="POST",
    ).create_api_gateway_response()

    actual = lambda_handler(test_event, context)
    assert actual == expected


@pytest.fixture
def mock_feedback_service(mocker):
    mocked_class = mocker.patch("handlers.send_feedback_handler.SendFeedbackService")
    mocked_instance = mocked_class.return_value
    return mocked_instance
