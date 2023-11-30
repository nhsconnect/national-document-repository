import json
import os
from unittest.mock import patch

import jwt
import pytest
from botocore.exceptions import ClientError
from enums.repository_role import RepositoryRole
from handlers.token_handler import lambda_handler
from models.oidc_models import IdTokenClaimSet
from services.ods_api_service import OdsApiService
from services.oidc_service import OidcService
from utils.audit_logging_setup import LoggingService
from utils.exceptions import AuthorisationException
from utils.lambda_response import ApiGatewayResponse


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
def mock_oidc_service(mocker, mock_userinfo):
    mocker.patch.object(OidcService, "__init__", return_value=None)
    mocker.patch.object(OidcService, "set_up_oidc_parameters", return_value=None)
    mocked_fetch_token = mocker.patch.object(OidcService, "fetch_tokens")
    mocked_fetch_user_org_codes = mocker.patch.object(
        OidcService, "fetch_user_org_codes"
    )

    mocked_tokens = [
        "fake_access_token",
        IdTokenClaimSet(
            sid="fake_cis2_session_id",
            sub="fake_cis2_user_id",
            exp=12345678,
            selected_roleid="1234",
        ),
    ]
    mocked_fetch_token.return_value = mocked_tokens
    mocked_fetch_user_org_codes.return_value = ["mock_ods_code1"]

    mocked_fetch_user_info = mocker.patch.object(OidcService, "fetch_userinfo")
    mocked_fetch_user_info.return_value = mock_userinfo

    mocked_fetch_user_role_code = mocker.patch.object(
        OidcService, "fetch_user_role_code"
    )
    mocked_fetch_user_role_code.return_value = ("R8008", "500000000000")

    yield {
        "fetch_token": mocked_fetch_token,
        "fetch_user_org_codes": mocked_fetch_user_org_codes,
        "fetch_user_role_code": mocked_fetch_user_role_code,
        "fetch_user_info": mocked_fetch_user_info,
    }


@pytest.fixture
def mock_ods_api_service(mocker):
    return_val = {
        "name": "PORTWAY LIFESTYLE CENTRE",
        "org_ods_code": "A9A5A",
        "role_code": "RO76",
    }

    mock = mocker.patch.object(
        OdsApiService, "fetch_organisation_with_permitted_role", return_value=return_val
    )

    yield mock


@pytest.fixture
def mock_jwt_encode(mocker):
    yield mocker.patch("jwt.encode", return_value="test_ndr_auth_token")


@pytest.fixture
def mock_logging_service(mocker):
    yield mocker.patch.object(LoggingService, "__init__", return_value=None)


def test_lambda_handler_respond_with_200_including_org_info_and_auth_token(
    set_env,
    mock_aws_infras,
    mock_oidc_service,
    mock_ods_api_service,
    mock_jwt_encode,
    mock_logging_service,
    mocker,
    context,
):
    mocker.patch(
        "handlers.token_handler.create_login_session",
        return_value="new_item_session_id",
    )
    mocker.patch(
        "handlers.token_handler.generate_repository_role",
        return_value=RepositoryRole.PCSE,
    )
    mocker.patch(
        "handlers.token_handler.issue_auth_token", return_value="mock_ndr_auth_token"
    )

    auth_code = "auth_code"
    test_event = {
        "queryStringParameters": {"code": auth_code, "state": "test_state"},
        "httpmethod": "GET",
    }

    expected_response_body = {
        "role": "PCSE",
        "authorisation_token": "mock_ndr_auth_token",
    }
    expected = ApiGatewayResponse(
        200, json.dumps(expected_response_body), "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(test_event, context)

    assert actual == expected

    mock_oidc_service["fetch_token"].expect_called_with(auth_code)


def test_lambda_handler_respond_with_400_if_state_or_auth_code_missing(
    mock_oidc_service, mock_aws_infras, set_env, context
):
    expected = ApiGatewayResponse(
        400, "Please supply an authorisation code and state", "GET"
    ).create_api_gateway_response()

    missing_state = {"queryStringParameters": {"code": "some_auth_code"}}
    missing_auth_code = {"queryStringParameters": {"state": "some_state"}}
    missing_both = {"queryStringParameters": {}}

    state_is_blank_string = {
        "queryStringParameters": {"code": "some_auth_code", "state": ""}
    }
    code_is_blank_string = {
        "queryStringParameters": {"code": "", "state": "some_state"}
    }
    both_are_blank_string = {"queryStringParameters": {"code": "", "state": ""}}

    empty_event = {}

    all_test_cases = [
        missing_state,
        missing_auth_code,
        missing_both,
        state_is_blank_string,
        code_is_blank_string,
        both_are_blank_string,
        empty_event,
    ]

    for test_event in all_test_cases:
        actual = lambda_handler(test_event, context)

        assert actual == expected
        mock_oidc_service["fetch_token"].assert_not_called()
        mock_oidc_service["fetch_user_org_codes"].assert_not_called()
        mock_aws_infras["session_table"].post.assert_not_called()


def test_lambda_handler_respond_with_401_when_auth_code_is_invalid(
    mock_aws_infras,
    mock_oidc_service,
    mock_ods_api_service,
    mock_jwt_encode,
    set_env,
    context,
):
    mock_oidc_service["fetch_token"].side_effect = AuthorisationException

    test_event = {
        "queryStringParameters": {"code": "invalid_token", "state": "test_state"}
    }

    expected = ApiGatewayResponse(
        401, "Failed to authenticate user with OIDC service", "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(test_event, context)

    assert actual == expected

    mock_oidc_service["fetch_user_org_codes"].assert_not_called()
    mock_aws_infras["session_table"].post.assert_not_called()


def test_lambda_handler_respond_with_400_when_given_state_not_found_in_state_table(
    mock_aws_infras, mock_oidc_service, set_env, context
):
    invalid_state = "state_not_exist_in_dynamo_db"
    test_event = {
        "queryStringParameters": {"code": "test_auth_code", "state": invalid_state}
    }

    mock_aws_infras["state_table"].query.return_value = {"Count": 0, "Items": []}

    expected = ApiGatewayResponse(
        400,
        "Failed to authenticate user",
        "GET",
    ).create_api_gateway_response()

    actual = lambda_handler(test_event, context)

    assert actual == expected

    mock_oidc_service["fetch_token"].assert_not_called()
    mock_oidc_service["fetch_user_org_codes"].assert_not_called()
    mock_aws_infras["session_table"].post.assert_not_called()


def test_lambda_handler_respond_with_401_when_user_dont_have_a_valid_role_to_login(
    mock_aws_infras,
    mock_oidc_service,
    # mock_ods_api_service,
    mock_jwt_encode,
    mocker,
    context,
):
    test_event = {
        "queryStringParameters": {"code": "test_auth_code", "state": "test_state"}
    }

    class PermittedOrgs:
        def keys(self):
            return []

    mocker.patch(
        "services.ods_api_service.OdsApiService.fetch_organisation_with_permitted_role"
    ).return_value = PermittedOrgs()

    expected = ApiGatewayResponse(
        401, "Failed to authenticate user with OIDC service", "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(test_event, context)

    assert actual == expected
    mock_aws_infras["session_table"].post.assert_not_called()


def test_lambda_handler_respond_with_500_when_encounter_boto3_error(
    mock_aws_infras, set_env, mocker, context
):
    test_event = {
        "queryStringParameters": {"code": "test_auth_code", "state": "test_state"}
    }
    mock_aws_infras["state_table"].query.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "mocked error"}}, "test"
    )

    mock_oidc = mocker.patch("services.oidc_service.OidcService.fetch_oidc_parameters")
    mock_oidc.return_value = {
        "OIDC_CLIENT_ID": "client-id",
        "OIDC_CLIENT_SECRET": "client-secret",
        "OIDC_ISSUER_URL": "https://issuer-url.com",
        "OIDC_TOKEN_URL": "https://token-url.com",
        "OIDC_USER_INFO_URL": "https://userinfo-url.com",
        "OIDC_JWKS_URL": "https://jwks-url.com",
        "OIDC_CALLBACK_URL": "https://callback-url.com",
    }

    expected = ApiGatewayResponse(
        500, "Server error", "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(test_event, context)

    assert actual == expected


def test_lambda_handler_respond_with_500_when_encounter_pyjwt_encode_error(
    mock_aws_infras,
    mock_oidc_service,
    mock_ods_api_service,
    mock_jwt_encode,
    set_env,
    context,
    mocker,
):
    test_event = {
        "queryStringParameters": {"code": "test_auth_code", "state": "test_state"}
    }

    jwt_error = jwt.PyJWTError()

    expected = ApiGatewayResponse(
        500, "Server error", "GET"
    ).create_api_gateway_response()
    with patch.object(OidcService, "fetch_tokens", side_effect=jwt_error):
        actual = lambda_handler(test_event, context)

    assert actual == expected
