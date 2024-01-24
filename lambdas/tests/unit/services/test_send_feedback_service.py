import boto3
import pytest
from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from models.feedback_model import Feedback
from services.base.ssm_service import SSMService
from services.send_feedback_service import SendFeedbackService
from tests.unit.conftest import (
    MOCK_FEEDBACK_EMAIL_SUBJECT,
    MOCK_FEEDBACK_RECIPIENT_EMAIL_LIST,
    MOCK_FEEDBACK_SENDER_EMAIL,
)
from tests.unit.helpers.data.feedback.mock_data import (
    MOCK_EMAIL_BODY,
    MOCK_PARSED_FEEDBACK,
    MOCK_PARSED_FEEDBACK_ANONYMOUS,
    MOCK_VALID_FEEDBACK_BODY_JSON_STR,
)
from utils.lambda_exceptions import SendFeedbackException


def test_process_feedback_validate_feedback_content_and_send_email(
    send_feedback_service, mock_send_feedback_by_email, mock_ses_client, mock_validator
):
    mock_event_body = MOCK_VALID_FEEDBACK_BODY_JSON_STR
    send_feedback_service.ses_client = mock_ses_client
    expected_email_body = MOCK_EMAIL_BODY

    send_feedback_service.process_feedback(mock_event_body)

    mock_validator.assert_called_with(mock_event_body)
    mock_send_feedback_by_email.assert_called_with(expected_email_body)


def test_process_feedback_raise_error_when_given_invalid_data(
    send_feedback_service, mock_send_feedback_by_email
):
    mock_event_body = '{"key1": "value1"}'
    expected_error = SendFeedbackException(400, LambdaError.FeedbackInvalidBody)

    with pytest.raises(SendFeedbackException) as error:
        send_feedback_service.process_feedback(mock_event_body)

    assert error.value == expected_error

    mock_send_feedback_by_email.assert_not_called()


def test_process_feedback_raise_error_when_fail_to_send_email_by_ses(
    send_feedback_service, mock_ses_client
):
    mock_error = ClientError(
        {
            "Error": {
                "Code": "LimitExceededException",
                "Message": "API call limit exceeded",
            }
        },
        "SendEmail",
    )
    mock_ses_client.send_email.side_effect = mock_error
    send_feedback_service.ses_client = mock_ses_client

    expected_error = SendFeedbackException(500, LambdaError.FeedbackSESFailure)
    event_body = MOCK_VALID_FEEDBACK_BODY_JSON_STR

    with pytest.raises(SendFeedbackException) as error:
        send_feedback_service.process_feedback(event_body)

    assert error.value == expected_error


def test_build_email_body_convert_feedback_to_html(send_feedback_service):
    expected = (
        "<html><body>"
        + "<h2>Name</h2><p>Jane Smith</p>"
        + "<h2>Email Address</h2><p>jane_smith@test-email.com</p>"
        + "<h2>Feedback</h2><p>Mock feedback content</p>"
        + "<h2>Overall Experience</h2><p>Very Satisfied</p>"
        + "</html></body>"
    )

    actual = send_feedback_service.build_email_body(MOCK_PARSED_FEEDBACK)

    assert actual == expected


def test_build_email_body_skip_name_and_email_if_not_given(send_feedback_service):
    expected = (
        "<html><body>"
        + "<h2>Feedback</h2><p>Mock feedback content</p>"
        + "<h2>Overall Experience</h2><p>Very Satisfied</p>"
        + "</html></body>"
    )

    actual = send_feedback_service.build_email_body(MOCK_PARSED_FEEDBACK_ANONYMOUS)

    assert actual == expected


def test_send_feedback_by_email_happy_path(send_feedback_service, mock_ses_client):
    send_feedback_service.ses_client = mock_ses_client

    send_feedback_service.send_feedback_by_email(MOCK_EMAIL_BODY)

    mock_ses_client.send_email.assert_called_with(
        Source=MOCK_FEEDBACK_SENDER_EMAIL,
        Destination={"ToAddresses": MOCK_FEEDBACK_RECIPIENT_EMAIL_LIST},
        Message={
            "Subject": {"Data": MOCK_FEEDBACK_EMAIL_SUBJECT},
            "Body": {"Html": {"Data": MOCK_EMAIL_BODY}},
        },
    )


def test_send_feedback_by_email_raise_error_on_failure(
    send_feedback_service, mock_ses_client
):
    mock_error = ClientError(
        {
            "Error": {
                "Code": "LimitExceededException",
                "Message": "API call limit exceeded",
            }
        },
        "SendEmail",
    )
    mock_ses_client.send_email.side_effect = mock_error
    send_feedback_service.ses_client = mock_ses_client

    expected_error = SendFeedbackException(500, LambdaError.FeedbackSESFailure)
    email_body = MOCK_EMAIL_BODY

    with pytest.raises(SendFeedbackException) as error:
        send_feedback_service.send_feedback_by_email(email_body)

    assert error.value == expected_error


def test_get_email_recipients_list_fetch_parameter_from_ssm_param_store(
    mock_get_ssm_parameter,
):
    mock_get_ssm_parameter.return_value = "gp2gp@localhost,test_email@localhost"

    actual = SendFeedbackService.get_email_recipients_list()
    expected = ["gp2gp@localhost", "test_email@localhost"]

    assert actual == expected


def test_get_email_parameters_raise_error_when_fail_to_fetch_from_ssm(
    mock_get_ssm_parameter,
):
    mock_error = ClientError(
        {
            "Error": {
                "Code": "UnauthorizedException",
                "Message": "Not authorized to access parameter store",
            }
        },
        "GetParameter",
    )
    expected_lambda_error = SendFeedbackException(
        500, LambdaError.FeedbackFetchParamFailure
    )

    mock_get_ssm_parameter.side_effect = mock_error

    with pytest.raises(SendFeedbackException) as error:
        SendFeedbackService.get_email_recipients_list()

    assert error.value == expected_lambda_error


#
#
# MOCK_SENDER_EMAIL = "feedback@localhost"
# MOCK_RECIPIENT_EMAIL_LIST = "gp2gp@localhost,test_email@localhost"
# MOCK_EMAIL_SUBJECT = "Digitised Lloyd George feedback"
#


@pytest.fixture
def mock_get_ssm_parameter(mocker):
    yield mocker.patch.object(SSMService, "get_ssm_parameter")


@pytest.fixture
def send_feedback_service(mocker, set_env):
    mocker.patch.object(
        SendFeedbackService,
        "get_email_recipients_list",
        return_value=MOCK_FEEDBACK_RECIPIENT_EMAIL_LIST,
    )
    return SendFeedbackService()


@pytest.fixture
def mock_send_feedback_by_email(mocker):
    yield mocker.patch.object(SendFeedbackService, "send_feedback_by_email")


@pytest.fixture
def mock_validator(mocker):
    yield mocker.patch.object(
        Feedback, "model_validate_json", return_value=MOCK_PARSED_FEEDBACK
    )


@pytest.fixture
def mock_ses_client(mocker):
    yield mocker.create_autospec(boto3.client("ses"))
