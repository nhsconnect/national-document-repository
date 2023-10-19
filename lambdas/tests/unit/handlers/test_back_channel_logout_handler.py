import json

from botocore.exceptions import ClientError
import pytest
from handlers.back_channel_logout_handler import lambda_handler
from services.oidc_service import OidcService
from utils.exceptions import AuthorisationException
from utils.lambda_response import ApiGatewayResponse


@pytest.fixture
def mock_oidc_service(mocker):
    mocker.patch.object(
        OidcService,
        "__init__",
        return_value=None)
    mock_oidc_service = mocker.patch.object(
        OidcService,
        "validate_and_decode_token")
    yield mock_oidc_service


def test_returns_500_when_env_vars_not_set():
    mock_token = "mock_token"
    expected = ApiGatewayResponse(
        500,
        "An error occurred due to missing key: 'OIDC_CALLBACK_URL'",
        "POST",
    ).create_api_gateway_response()
    actual = lambda_handler(build_event_from_token(mock_token), None)

    assert actual == expected


def test_back_channel_logout_handler_valid_jwt_returns_200_if_session_exists(mocker, mock_oidc_service, monkeypatch,
                                                                             context):
    monkeypatch.setenv("OIDC_CALLBACK_URL", "mock_url")
    mock_token = "mock_token"
    mock_session_id = "mock_session_id"
    mock_decoded_token = {"sid": mock_session_id}
    mock_oidc_service.return_value = mock_decoded_token
    mock_dynamo_service = mocker.patch(
        "handlers.back_channel_logout_handler.remove_session_from_dynamo_db"
    )

    expected = ApiGatewayResponse(200, "", "POST").create_api_gateway_response()

    actual = lambda_handler(build_event_from_token(mock_token), context)

    assert expected == actual
    mock_oidc_service.asset_called_with(mock_token)
    mock_dynamo_service.assert_called_with(mock_session_id)


def test_back_channel_logout_handler_missing_jwt_returns_400(mocker, mock_oidc_service, monkeypatch,
                                                             context):
    monkeypatch.setenv("OIDC_CALLBACK_URL", "mock_url")
    mock_token = "mock_token"
    event = {
        "httpMethod": "POST",
        "body": "{}"
    }
    expected = ApiGatewayResponse(400, "An error occurred due to missing key: 'logout_token'",
                                  "POST").create_api_gateway_response()

    actual = lambda_handler(event, context)

    assert expected == actual


def test_back_channel_logout_handler_jwt_without_session_id_returns_400(mock_oidc_service, monkeypatch):
    monkeypatch.setenv("OIDC_CALLBACK_URL", "mock_url")
    mock_token = "mock_token"
    mock_session_id = "mock_session_id"
    mock_decoded_token = {"not_an_sid": mock_session_id}
    mock_oidc_service.return_value = mock_decoded_token

    expected = ApiGatewayResponse(
        400, """{ "error":"No sid field in decoded token"}""", "POST"
    ).create_api_gateway_response()

    actual = lambda_handler(build_event_from_token(mock_token), None)

    assert expected == actual
    mock_oidc_service.asset_called_with(mock_token)


def test_back_channel_logout_handler_invalid_jwt_returns_400(mock_oidc_service, monkeypatch):
    monkeypatch.setenv("OIDC_CALLBACK_URL", "mock_url")
    mock_token = "mock_token"
    mock_oidc_service.side_effect = AuthorisationException

    expected = ApiGatewayResponse(
        400, """{ "error":"JWT was invalid"}""", "POST"
    ).create_api_gateway_response()

    actual = lambda_handler(build_event_from_token(mock_token), None)

    assert expected == actual
    mock_oidc_service.asset_called_with(mock_token)


def test_back_channel_logout_handler_boto_error_returns_400(mocker, mock_oidc_service, monkeypatch):
    monkeypatch.setenv("OIDC_CALLBACK_URL", "mock_url")
    mock_token = "mock_token"
    mock_session_id = "mock_session_id"
    mock_decoded_token = {"sid": mock_session_id}
    mock_oidc_service.return_value = mock_decoded_token
    mock_dynamo_service = mocker.patch(
        "handlers.back_channel_logout_handler.remove_session_from_dynamo_db",
        side_effect=ClientError(
            {"Error": {"Code": "500", "Message": "mocked error"}}, "test"
        ),
    )

    expected = ApiGatewayResponse(
        400, """{ "error":"Internal error logging user out"}""", "POST"
    ).create_api_gateway_response()

    actual = lambda_handler(build_event_from_token(mock_token), None)

    assert expected == actual
    mock_oidc_service.asset_called_with(mock_token)
    mock_dynamo_service.assert_called_with(mock_session_id)


def build_event_from_token(token: str) -> dict:
    body_string = {"logout_token": token}
    return {
        "httpMethod": "POST",
        "body": json.dumps(body_string)
    }
