from unittest.mock import MagicMock

from jwt import PyJWTError
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.request_context import request_context

actual_lambda_logic = MagicMock()


@set_request_context_for_logging
def lambda_handler(event, context):
    actual_lambda_logic()
    return "200 OK"


def test_set_request_context_for_logging_request_id_and_auth_are_found(
    mocker, event, context
):
    mock_session_id = "mock_session_id"
    mock_decoded_token = {"ndr_session_id": mock_session_id}
    mock_token_validator = mocker.patch("jwt.decode", return_value=mock_decoded_token)

    lambda_handler(event, context)

    assert request_context.request_id == context.aws_request_id
    assert request_context.authorization == mock_decoded_token
    mock_token_validator.assert_called_with(
        "test_token", algorithms=["RS256"], options={"verify_signature": False}
    )


def test_set_request_context_for_logging_missing_auth(
    mocker, invalid_nhs_number_event, context
):
    mock_token_validator = mocker.patch("jwt.decode")

    lambda_handler(invalid_nhs_number_event, context)

    assert request_context.request_id == context.aws_request_id
    assert request_context.authorization is None
    mock_token_validator.assert_not_called()


def test_set_request_context_for_logging_invalid_auth(mocker, event, context):
    mock_token_validator = mocker.patch("jwt.decode", side_effect=PyJWTError())

    lambda_handler(event, context)

    assert request_context.request_id == context.aws_request_id
    assert request_context.authorization is None
    mock_token_validator.assert_called_with(
        "test_token", algorithms=["RS256"], options={"verify_signature": False}
    )
