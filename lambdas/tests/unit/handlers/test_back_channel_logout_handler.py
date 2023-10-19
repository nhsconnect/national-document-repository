import json
from botocore.exceptions import ClientError
import pytest
from handlers.back_channel_logout_handler import lambda_handler
from services.oidc_service import OidcService
from utils.exceptions import AuthorisationException
from tests.unit.helpers.ssm_responses import \
    MOCK_SINGLE_SECURE_STRING_PARAMETER_RESPONSE
from utils.lambda_response import ApiGatewayResponse

@pytest.fixture
def mock_oidc_service(mocker):
    mocker.patch.object(
        OidcService, 
        "__init__", 
        return_value = None)
    mock_oidc_service = mocker.patch.object(
        OidcService, 
        "validate_and_decode_token")
    yield mock_oidc_service

# def test_back_channel_logout_handler_valid_jwt_returns_200_if_session_exists(mocker, mock_oidc_service):
#     mock_token = json.dumps("mock_token")
#     mock_request = "logout_token=" + mock_token
#     mock_session_id = "mock_session_id"
#     mock_decoded_token = {"sid": mock_session_id}
#     mock_oidc_service.return_value = mock_decoded_token
#     mock_dynamo_service = mocker.patch(
#         "handlers.back_channel_logout_handler.remove_session_from_dynamo_db"
#     )

#     expected = ApiGatewayResponse(200, "", "GET").create_api_gateway_response()

#     actual = lambda_handler(build_event_from_token(mock_request), None)

#     assert expected == actual
#     mock_oidc_service.asset_called_with(mock_token)
#     mock_dynamo_service.assert_called_with(mock_session_id)


# def test_back_channel_logout_handler_jwt_without_session_id_returns_400(mock_oidc_service):
#     mock_token = "mock_token"
#     mock_session_id = "mock_session_id"
#     mock_decoded_token = {"not_an_sid": mock_session_id}
#     mock_oidc_service.return_value = mock_decoded_token

#     expected = ApiGatewayResponse(
#         400,  """{ "error":"No sid field in decoded token"}""", "GET"
#     ).create_api_gateway_response()

#     actual = lambda_handler(build_event_from_token(mock_token), None)

#     assert expected == actual
#     mock_oidc_service.asset_called_with(mock_token)


# def test_back_channel_logout_handler_invalid_jwt_returns_400(mock_oidc_service):
#     mock_token = "mock_token"
#     mock_session_id = "mock_session_id"
#     mock_oidc_service.side_effect=AuthorisationException

#     expected = ApiGatewayResponse(
#         400,  """{ "error":"JWT was invalid"}""", "GET"
#     ).create_api_gateway_response()

#     actual = lambda_handler(build_event_from_token(mock_token), None)

#     assert expected == actual
#     mock_oidc_service.asset_called_with(mock_token)


# def test_back_channel_logout_handler_boto_error_returns_400(mocker, mock_oidc_service):
#     mock_token = "mock_token"
#     mock_session_id = "mock_session_id"
#     mock_decoded_token = {"sid": mock_session_id}
#     mock_oidc_service.return_value = mock_decoded_token
#     mock_dynamo_service = mocker.patch(
#         "handlers.back_channel_logout_handler.remove_session_from_dynamo_db",
#         side_effect=ClientError(
#             {"Error": {"Code": "500", "Message": "mocked error"}}, "test"
#         ),
#     )

#     expected = ApiGatewayResponse(
#         400, """{ "error":"Internal error logging user out"}""", "GET"
#     ).create_api_gateway_response()

#     actual = lambda_handler(build_event_from_token(mock_token), None)

#     assert expected == actual
#     mock_oidc_service.asset_called_with(mock_token)
#     mock_dynamo_service.assert_called_with(mock_session_id)


# def build_event_from_token(token: str) -> dict:
#     return {"body": {"logout_token": token}}
