import json
from enum import Enum

import pytest
from enums.lambda_error import LambdaError
from handlers.login_redirect_handler import lambda_handler
from utils.lambda_exceptions import LoginRedirectException


class MockError(Enum):
    Error = {
        "message": "Client error",
        "err_code": "AB_XXXX",
        "interaction_id": "88888888-4444-4444-4444-121212121212",
    }


@pytest.fixture
def mock_configuration_service(mocker):
    mock_service = mocker.patch(
        "handlers.login_redirect_handler.DynamicConfigurationService"
    )
    yield mock_service


def test_login_redirect_lambda_handler_valid(
    mocker, set_env, event, context, mock_configuration_service
):
    mock_login_service_object = mocker.MagicMock()
    mocker.patch(
        "handlers.login_redirect_handler.LoginRedirectService",
        return_value=mock_login_service_object,
    )

    response = lambda_handler(event, context)
    mock_login_service_object.prepare_redirect_response.assert_called_once()
    assert response["statusCode"] == 303
    assert response["body"] == ""


def test_login_redirect_lambda_handler_exception(
    mocker, set_env, event, context, mock_configuration_service
):
    mock_login_service_object = mocker.MagicMock()
    mocker.patch(
        "handlers.login_redirect_handler.LoginRedirectService",
        return_value=mock_login_service_object,
    )
    mock_login_service_object.prepare_redirect_response.side_effect = (
        LoginRedirectException(500, LambdaError.MockError)
    )

    expected_err = MockError.Error.value["err_code"]
    expected_message = MockError.Error.value["message"]
    response = lambda_handler(event, context)

    expected_body = json.loads(response["body"])
    mock_login_service_object.prepare_redirect_response.assert_called_once()
    assert response["statusCode"] == 500
    assert expected_body["message"] == expected_message
    assert expected_body["err_code"] == expected_err
