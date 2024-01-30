import json

import pytest
from enums.lambda_error import LambdaError
from handlers.send_feedback_handler import lambda_handler
from services.send_feedback_service import SendFeedbackService
from tests.unit.conftest import MOCK_FEEDBACK_RECIPIENT_EMAIL_LIST, MOCK_INTERACTION_ID
from tests.unit.helpers.data.feedback.mock_data import MOCK_VALID_SEND_FEEDBACK_EVENT
from utils.lambda_exceptions import SendFeedbackException
from utils.lambda_response import ApiGatewayResponse


@pytest.fixture
def mock_feedback_service(mocker):
    mocked_class = mocker.patch("handlers.send_feedback_handler.SendFeedbackService")
    mocked_instance = mocked_class.return_value
    return mocked_instance


@pytest.fixture
def mock_get_email_recipients_list(mocker):
    yield mocker.patch.object(
        SendFeedbackService,
        "get_email_recipients_list",
        return_value=MOCK_FEEDBACK_RECIPIENT_EMAIL_LIST,
    )


def test_lambda_handler_respond_with_200_when_successful(
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
            {
                "message": "Missing POST request body",
                "err_code": "SFB_4001",
                "interaction_id": MOCK_INTERACTION_ID,
            }
        ),
        methods="POST",
    ).create_api_gateway_response()

    actual = lambda_handler(test_event, context)
    assert actual == expected


def test_lambda_handler_respond_with_400_when_invalid_event_body_given(
    set_env, context, mock_get_email_recipients_list
):
    test_event = {"body": "some_invalid_event_body", "httpMethod": "POST"}
    expected = ApiGatewayResponse(
        status_code=400,
        body=json.dumps(
            {
                "message": "Invalid POST request body",
                "err_code": "SFB_4002",
                "interaction_id": MOCK_INTERACTION_ID,
            }
        ),
        methods="POST",
    ).create_api_gateway_response()

    actual = lambda_handler(test_event, context)
    assert actual == expected


def test_lambda_handler_respond_with_500_when_missing_env_var(context):
    test_event = MOCK_VALID_SEND_FEEDBACK_EVENT
    expected = ApiGatewayResponse(
        status_code=500,
        body=json.dumps(
            {
                "message": "An error occurred due to missing environment variable: 'FROM_EMAIL_ADDRESS'",
                "err_code": "ENV_5001",
                "interaction_id": MOCK_INTERACTION_ID,
            }
        ),
        methods="POST",
    ).create_api_gateway_response()

    actual = lambda_handler(test_event, context)
    assert actual == expected


def test_lambda_handler_respond_with_500_when_failed_to_get_recipient_emails_from_param_store(
    set_env, context, mock_get_email_recipients_list
):
    test_event = MOCK_VALID_SEND_FEEDBACK_EVENT
    mock_get_email_recipients_list.side_effect = SendFeedbackException(
        500, LambdaError.FeedbackFetchParamFailure
    )

    expected = ApiGatewayResponse(
        status_code=500,
        body=json.dumps(
            {
                "message": "Failed to fetch parameters for sending email from SSM param store",
                "err_code": "SFB_5002",
                "interaction_id": MOCK_INTERACTION_ID,
            }
        ),
        methods="POST",
    ).create_api_gateway_response()

    actual = lambda_handler(test_event, context)
    assert actual == expected


def test_lambda_handler_respond_with_500_when_failed_to_send_email(
    set_env, context, mock_feedback_service
):
    test_event = MOCK_VALID_SEND_FEEDBACK_EVENT
    mock_feedback_service.process_feedback.side_effect = SendFeedbackException(
        500, LambdaError.FeedbackSESFailure
    )

    expected = ApiGatewayResponse(
        status_code=500,
        body=json.dumps(
            {
                "message": "Error occur when sending email by SES",
                "err_code": "SFB_5001",
                "interaction_id": MOCK_INTERACTION_ID,
            }
        ),
        methods="POST",
    ).create_api_gateway_response()

    actual = lambda_handler(test_event, context)
    assert actual == expected
