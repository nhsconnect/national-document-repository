from handlers.logout_handler import logout_handler
from utils.lambda_response import ApiGatewayResponse
from jwt.exceptions import PyJWTError
from botocore.exceptions import ClientError
from tests.unit.helpers.ssm_responses import MOCK_SINGLE_SECURE_STRING_PARAMETER_RESPONSE

def test_logout_handler_valid_jwt_returns_200(mocker, monkeypatch):
    mock_token = "mock_token"
    mock_session_id = "mock_session_id"
    mock_decoded_token = {"ndr_session_id":mock_session_id}
    monkeypatch.setenv("SSM_PARAM_JWT_TOKEN_PUBLIC_KEY", "mock_public_key")
    mock_token_validator = mocker.patch("jwt.decode", return_value=mock_decoded_token)
    mock_dynamo_service = mocker.patch("handlers.logout_handler.remove_session_from_dynamo_db")
    mock_ssm_service = mocker.patch("handlers.logout_handler.get_ssm_parameter", return_value=MOCK_SINGLE_SECURE_STRING_PARAMETER_RESPONSE)

    expected = ApiGatewayResponse(
        200, "", "GET"
    ).create_api_gateway_response()

    actual = logout_handler(mock_token)

    assert expected == actual
    mock_token_validator.asset_called_with(mock_token)
    mock_dynamo_service.assert_called_with(mock_session_id)
    mock_ssm_service.assert_called_once()

def test_logout_handler_invalid_jwt_returns_500(mocker, monkeypatch):
    mock_token = "mock_token"
    monkeypatch.setenv("SSM_PARAM_JWT_TOKEN_PUBLIC_KEY", "mock_public_key")
    mock_token_validator = mocker.patch("jwt.decode", side_effect = PyJWTError())
    mock_ssm_service = mocker.patch("handlers.logout_handler.get_ssm_parameter", return_value=MOCK_SINGLE_SECURE_STRING_PARAMETER_RESPONSE)

    expected = ApiGatewayResponse(
        500, "Error logging user out", "GET"
    ).create_api_gateway_response()

    actual = logout_handler(mock_token)

    assert expected == actual
    mock_token_validator.asset_called_with(mock_token)
    mock_ssm_service.assert_called_once()


def test_logout_handler_boto_error_returns_500(mocker, monkeypatch):
    mock_token = "mock_token"
    mock_session_id = "mock_session_id"
    mock_decoded_token = {"ndr_session_id":mock_session_id}
    monkeypatch.setenv("SSM_PARAM_JWT_TOKEN_PUBLIC_KEY", "mock_public_key")
    mock_token_validator = mocker.patch("jwt.decode", return_value=mock_decoded_token)
    mock_dynamo_service = mocker.patch("handlers.logout_handler.remove_session_from_dynamo_db", side_effect = ClientError({'Error': {'code' : 500, 'message' : 'mocked error'}}, 'test'))
    mock_ssm_service = mocker.patch("handlers.logout_handler.get_ssm_parameter", return_value=MOCK_SINGLE_SECURE_STRING_PARAMETER_RESPONSE)

    expected = ApiGatewayResponse(
        500, "Error logging user out", "GET"
    ).create_api_gateway_response()

    actual = logout_handler(mock_token)

    assert expected == actual
    mock_token_validator.asset_called_with(mock_token)
    mock_dynamo_service.assert_called_with(mock_session_id)
    mock_ssm_service.assert_called_once()