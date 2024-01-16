from handlers.login_redirect_handler import lambda_handler
from utils.lambda_exceptions import LoginRedirectException
import json

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
        side_effect=LoginRedirectException(500, "LR_5001", "test"),
    )

    response = lambda_handler(event, context)

    mock_prepare_redirect_response.assert_called_once()
    
    responseBody = json.loads(response["body"] )
    assert response["statusCode"] == 500
    assert responseBody["message"] == "test"
    assert responseBody["errCode"] == "LR_5001"
