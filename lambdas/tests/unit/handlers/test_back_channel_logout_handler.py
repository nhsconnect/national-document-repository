from botocore.exceptions import ClientError
from handlers.back_channel_logout_handler import lambda_handler
from jwt.exceptions import PyJWTError
from tests.unit.helpers.ssm_responses import \
    MOCK_SINGLE_SECURE_STRING_PARAMETER_RESPONSE
from utils.lambda_response import ApiGatewayResponse


def test_back_channel_logout_handler_valid_jwt_returns_200_if_session_exists(mocker, monkeypatch):
    mock_token = "mock_token"
    mock_session_id = "mock_session_id"
    mock_decoded_token = {"sid": mock_session_id}
    mock_token_validator = mocker.patch("jwt.decode", return_value=mock_decoded_token)
    mock_ssm_service = mocker.patch(
        "handlers.back_channel_logout_handler.get_ssm_parameter", 
        return_value=MOCK_SINGLE_SECURE_STRING_PARAMETER_RESPONSE,
    )
    mock_dynamo_service = mocker.patch(
        "handlers.back_channel_logout_handler.remove_session_from_dynamo_db"
    )

    expected = ApiGatewayResponse(200, "", "GET").create_api_gateway_response()

    actual = lambda_handler(build_event_from_token(mock_token), None)

    assert expected == actual
    mock_token_validator.asset_called_with(mock_token)
    mock_dynamo_service.assert_called_with(mock_session_id)
    mock_ssm_service.assert_called_once_with("SSM_PARAM_CIS2_BCL_PUBLIC_KEY")


def test_back_channel_logout_handler_jwt_without_session_id_returns_400(mocker):
    mock_token = "mock_token"
    mock_token_validator = mocker.patch(
        "jwt.decode",
        return_value={"token_decode_correctly": "but_no_session_id_in_content"},
    )
    mock_ssm_service = mocker.patch(
        "handlers.back_channel_logout_handler.get_ssm_parameter",
        return_value=MOCK_SINGLE_SECURE_STRING_PARAMETER_RESPONSE,
    )

    expected = ApiGatewayResponse(
        400,  """{ "error":"Invalid x-auth header"}""", "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(build_event_from_token(mock_token), None)

    assert expected == actual
    mock_token_validator.asset_called_with(mock_token)
    mock_ssm_service.assert_called_once()


def test_back_channel_logout_handler_boto_error_returns_400(mocker):
    mock_token = "mock_token"
    mock_session_id = "mock_session_id"
    mock_decoded_token = {"sid": mock_session_id}
    mock_token_validator = mocker.patch("jwt.decode", return_value=mock_decoded_token)
    mock_dynamo_service = mocker.patch(
        "handlers.back_channel_logout_handler.remove_session_from_dynamo_db",
        side_effect=ClientError(
            {"Error": {"Code": "500", "Message": "mocked error"}}, "test"
        ),
    )
    mock_ssm_service = mocker.patch(
        "handlers.back_channel_logout_handler.get_ssm_parameter",
        return_value=MOCK_SINGLE_SECURE_STRING_PARAMETER_RESPONSE,
    )

    expected = ApiGatewayResponse(
        400, """{ "error":"Internal error logging user out"}""", "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(build_event_from_token(mock_token), None)

    assert expected == actual
    mock_token_validator.asset_called_with(mock_token)
    mock_dynamo_service.assert_called_with(mock_session_id)
    mock_ssm_service.assert_called_once()


def build_event_from_token(token: str) -> dict:
    return {"headers": {"x-auth": token}}
