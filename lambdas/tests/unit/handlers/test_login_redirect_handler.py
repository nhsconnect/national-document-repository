from handlers.login_redirect_handler import lambda_handler


def test_login_redirect_lambda_handler_valid(mocker, set_env, event, context):
    mock_prepare_redirect_response = mocker.patch(
        "services.login_redirect_service.LoginRedirectService.prepare_redirect_response"
    )

    response = lambda_handler(event, context)

    mock_prepare_redirect_response.assert_called_once()

    assert response["statusCode"] == 200
    assert response["body"] == "Bulk upload report creation successful"
