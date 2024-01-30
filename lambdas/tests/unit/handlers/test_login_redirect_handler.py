import json
from enum import Enum

from handlers.login_redirect_handler import lambda_handler
from utils.lambda_exceptions import LoginRedirectException


class MockError(Enum):
    Error = {
        "message": "Client error",
        "err_code": "AB_XXXX",
        "interaction_id": "88888888-4444-4444-4444-121212121212",
    }


def test_login_redirect_lambda_handler_valid(mocker, set_env, event, context):
    mock_prepare_redirect_response = mocker.patch(
        "services.login_redirect_service.LoginRedirectService.prepare_redirect_response"
    )

    response = lambda_handler(event, context)

    mock_prepare_redirect_response.assert_called_once()
    assert response["statusCode"] == 303
    assert response["body"] == ""


def test_login_redirect_lambda_handler_exception(mocker, set_env, event, context):
    mock_prepare_redirect_response = mocker.patch(
        "services.login_redirect_service.LoginRedirectService.prepare_redirect_response",
        side_effect=LoginRedirectException(500, MockError.Error),
    )

    expected_err = MockError.Error.value["err_code"]
    expected_message = MockError.Error.value["message"]
    response = lambda_handler(event, context)

    expected_body = json.loads(response["body"])
    mock_prepare_redirect_response.assert_called_once()
    assert response["statusCode"] == 500
    assert expected_body["message"] == expected_message
    assert expected_body["err_code"] == expected_err
