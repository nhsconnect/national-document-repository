import os

import pytest
from models.oidc_models import IdTokenClaimSet
from services.oidc_service import OidcService


@pytest.fixture
def mock_aws_infras(mocker, set_env):
    mock_dynamo = mocker.patch("boto3.resource")
    mock_state_table = mocker.MagicMock()
    mock_session_table = mocker.MagicMock()

    mock_ssm_client = mocker.patch("boto3.client")
    mock_ssm_client.return_value.get_parameter.return_value = {
        "Parameter": {"Value": "fake_private_key"}
    }

    mock_state_table.query.return_value = {"Count": 1, "Items": [{"id": "fake_item"}]}

    def mock_dynamo_table(table_name: str):
        if table_name == os.environ["AUTH_STATE_TABLE_NAME"]:
            return mock_state_table
        elif table_name == os.environ["AUTH_SESSION_TABLE_NAME"]:
            return mock_session_table
        else:
            raise RuntimeError("something went wrong with mocking")

    mock_dynamo.return_value.Table.side_effect = mock_dynamo_table

    yield {"state_table": mock_state_table, "session_table": mock_session_table}


@pytest.fixture
def mock_oidc_service(mocker):
    mocker.patch.object(OidcService, "__init__", return_value=None)
    mocked_fetch_token = mocker.patch.object(OidcService, "fetch_tokens")
    mocked_fetch_user_org_codes = mocker.patch.object(
        OidcService, "fetch_user_org_codes"
    )

    mocked_tokens = [
        "fake_access_token",
        IdTokenClaimSet(
            sid="fake_cis2_session_id", sub="fake_cis2_user_id", exp=12345678
        ),
    ]
    mocked_fetch_token.return_value = mocked_tokens
    mocked_fetch_user_org_codes.return_value = ["mock_ods_code1", "mock_ods_code2"]

    yield {
        "fetch_token": mocked_fetch_token,
        "fetch_user_org_codes": mocked_fetch_user_org_codes,
    }


@pytest.fixture
def mock_ods_api_service(mocker):
    mock = mocker.patch(
        "services.ods_api_service.OdsApiServiceForPassword"
    )

    mock.return_value.fetch_organisation_with_permitted_role.return_value = [
        {"org_name": "PORTWAY LIFESTYLE CENTRE", "ods_code": "A9A5A", "role": "DEV"}
    ]
    yield mock


@pytest.fixture
def mock_jwt_encode(mocker):
    yield mocker.patch("jwt.encode", return_value="test_ndr_auth_token")


# def test_lambda_handler_respond_with_200_and_org_info_and_auth_token(
#     set_env,
#     mock_aws_infras,
#     mock_oidc_service,
#     # mock_ods_api_service,
#     mock_jwt_encode,
#     mocker,
# ):
#     test_event = {
#         "queryStringParameters": {"code": "test_auth_code", "state": "test_state"},
#         "httpmethod": "GET",
#     }

#     expected_response_body = {
#         "organisations": [
#             {"org_name": "PORTWAY LIFESTYLE CENTRE", "ods_code": "A9A5A", "role": "DEV"}
#         ],
#         "authorisation_token": "test_ndr_auth_token",
#     }
#     expected = ApiGatewayResponse(
#         200, json.dumps(expected_response_body), "GET"
#     ).create_api_gateway_response()

#     mocker.patch(
#         "services.ods_api_service_for_password.OdsApiServiceForPassword.fetch_organisation_with_permitted_role"
#     ).return_value = [
#         {"org_name": "PORTWAY LIFESTYLE CENTRE", "ods_code": "A9A5A", "role": "DEV"}
#     ]

#     actual = lambda_handler(test_event, None)

#     assert actual == expected


# def test_lambda_handler_respond_with_400_if_state_or_auth_code_missing(
#     mock_oidc_service, mock_aws_infras, set_env
# ):
#     expected = ApiGatewayResponse(
#         400, "Please supply an authorisation code and state", "GET"
#     ).create_api_gateway_response()

#     missing_state = {"queryStringParameters": {"code": "some_auth_code"}}
#     missing_auth_code = {"queryStringParameters": {"state": "some_state"}}
#     missing_both = {"queryStringParameters": {}}

#     state_is_blank_string = {
#         "queryStringParameters": {"code": "some_auth_code", "state": ""}
#     }
#     code_is_blank_string = {
#         "queryStringParameters": {"code": "", "state": "some_state"}
#     }
#     both_are_blank_string = {"queryStringParameters": {"code": "", "state": ""}}

#     empty_event = {}

#     all_test_cases = [
#         missing_state,
#         missing_auth_code,
#         missing_both,
#         state_is_blank_string,
#         code_is_blank_string,
#         both_are_blank_string,
#         empty_event,
#     ]

#     for test_event in all_test_cases:
#         actual = lambda_handler(test_event, None)

#         assert actual == expected
#         mock_oidc_service["fetch_token"].assert_not_called()
#         mock_oidc_service["fetch_user_org_codes"].assert_not_called()
#         mock_aws_infras["session_table"].post.assert_not_called()


# def test_lambda_handler_respond_with_401_when_auth_code_is_invalid(
#     mock_aws_infras, mock_oidc_service, mock_ods_api_service, mock_jwt_encode, set_env
# ):
#     mock_oidc_service["fetch_token"].side_effect = AuthorisationException

#     test_event = {
#         "queryStringParameters": {"code": "invalid_token", "state": "test_state"}
#     }

#     expected = ApiGatewayResponse(
#         401, "Failed to authenticate user with OIDC service", "GET"
#     ).create_api_gateway_response()

#     actual = lambda_handler(test_event, None)

#     assert actual == expected

#     mock_oidc_service["fetch_user_org_codes"].assert_not_called()
#     mock_aws_infras["session_table"].post.assert_not_called()


# def test_lambda_handler_respond_with_400_when_given_state_not_found_in_state_table(
#     mock_aws_infras, mock_oidc_service, set_env
# ):
#     invalid_state = "state_not_exist_in_dynamo_db"
#     test_event = {
#         "queryStringParameters": {"code": "test_auth_code", "state": invalid_state}
#     }

#     mock_aws_infras["state_table"].query.return_value = {"Count": 0, "Items": []}

#     expected = ApiGatewayResponse(
#         400,
#         f"Mismatching state values. Cannot find state {invalid_state} in record",
#         "GET",
#     ).create_api_gateway_response()

#     actual = lambda_handler(test_event, None)

#     assert actual == expected

#     mock_oidc_service["fetch_token"].assert_not_called()
#     mock_oidc_service["fetch_user_org_codes"].assert_not_called()
#     mock_aws_infras["session_table"].post.assert_not_called()


# def test_lambda_handler_respond_with_401_when_user_dont_have_a_valid_role_to_login(
#     mock_aws_infras,
#     mock_oidc_service,
#     # mock_ods_api_service,
#     mock_jwt_encode,
#     mocker,
# ):
#     test_event = {
#         "queryStringParameters": {"code": "test_auth_code", "state": "test_state"}
#     }

#     mocker.patch(
#         "services.ods_api_service_for_password.OdsApiServiceForPassword.fetch_organisation_with_permitted_role"
#     ).return_value = []

#     expected = ApiGatewayResponse(
#         401, "Failed to authenticate user with OIDC service", "GET"
#     ).create_api_gateway_response()

#     actual = lambda_handler(test_event, None)

#     assert actual == expected
#     mock_aws_infras["session_table"].post.assert_not_called()


# def test_lambda_handler_respond_with_500_when_encounter_boto3_error(
#     mock_aws_infras, set_env, mocker
# ):
#     test_event = {
#         "queryStringParameters": {"code": "test_auth_code", "state": "test_state"}
#     }
#     mock_aws_infras["state_table"].query.side_effect = ClientError(
#         {"Error": {"Code": "500", "Message": "mocked error"}}, "test"
#     )

#     mock_oidc = mocker.patch(
#         "services.oidc_service_for_password.OidcServiceForPassword.fetch_oidc_parameters"
#     )
#     mock_oidc.return_value = {
#         "OIDC_CLIENT_ID": "client-id",
#         "OIDC_CLIENT_SECRET": "client-secret",
#         "OIDC_ISSUER_URL": "https://issuer-url.com",
#         "OIDC_TOKEN_URL": "https://token-url.com",
#         "OIDC_USER_INFO_URL": "https://userinfo-url.com",
#         "OIDC_JWKS_URL": "https://jwks-url.com",
#         "OIDC_CALLBACK_URL": "https://callback-url.com",
#     }

#     expected = ApiGatewayResponse(
#         500, "Server error", "GET"
#     ).create_api_gateway_response()

#     actual = lambda_handler(test_event, None)

#     assert actual == expected


# def test_lambda_handler_respond_with_500_when_encounter_pyjwt_encode_error(
#     mock_aws_infras,
#     mock_oidc_service,
#     mock_ods_api_service,
#     mock_jwt_encode,
#     set_env,
#     mocker,
# ):
#     test_event = {
#         "queryStringParameters": {"code": "test_auth_code", "state": "test_state"}
#     }

#     jwt_error = jwt.PyJWTError()

#     expected = ApiGatewayResponse(
#         500, "Server error", "GET"
#     ).create_api_gateway_response()
#     with patch.object(OidcServiceForPassword, "fetch_tokens", side_effect=jwt_error):
#         actual = lambda_handler(test_event, None)

#     assert actual == expected
