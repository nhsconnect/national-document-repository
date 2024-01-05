from services.token_service import TokenService


def test_get_public_key_and_decode_auth_token(mocker):
    mock_jwt_decode = mocker.patch("jwt.decode", return_value="decoded token")
    mocker.patch(
        "services.base.ssm_service.SSMService.get_ssm_parameter",
        return_value="test_value_param_key",
    )
    token_service = TokenService()
    response = token_service.get_public_key_and_decode_auth_token(
        auth_token="token_test", ssm_public_key_parameter="param_key"
    )

    assert response == "decoded token"
    mock_jwt_decode.assert_called_with(
        "token_test", "test_value_param_key", algorithms=["RS256"]
    )
