from services.token_service import TokenService

class FakeSSMService:
    def __init__(self, *arg, **kwargs):
        pass
    @staticmethod
    def get_ssm_parameter( parameter_key, *arg, **kwargs):
        return f"test_value_{parameter_key}"


def test_get_public_key_and_decode_auth_token(mocker):
    mock_jwt_decode = mocker.patch("jwt.decode", return_value="decoded token")

    token_service = TokenService(FakeSSMService)
    response = token_service.get_public_key_and_decode_auth_token(auth_token="token_test", ssm_public_key_parameter="param_key")

    assert response == "decoded token"
    mock_jwt_decode.assert_called_with("token_test", "test_value_param_key", algorithms=['RS256'])
