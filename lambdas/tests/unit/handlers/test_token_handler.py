import json
import os
from unittest.mock import patch

import pytest

from handlers.token_handler import lambda_handler
from models.oidc_models import IdTokenClaimSet
from services.ods_api_service import OdsApiService
from services.oidc_service import OidcService
from utils.exceptions import AuthorisationException
from utils.lambda_response import ApiGatewayResponse


def test__no_ssm_key():
    pass


PATCH_ENV_VAR = {
    "AUTH_STATE_TABLE_NAME": "test_state_table",
    "AUTH_SESSION_TABLE_NAME": "test_session_table",
}


@pytest.fixture
def patch_env_vars():
    with patch.dict(os.environ, PATCH_ENV_VAR):
        yield


@pytest.fixture
def mock_aws_infras(mocker):
    mock_dynamo = mocker.patch("boto3.resource")
    mock_state_table = mocker.MagicMock()
    mock_session_table = mocker.MagicMock()

    mock_ssm_client = mocker.patch("boto3.client")
    mock_ssm_client.return_value.get_parameter.return_value = {
        "Parameter": {"Value": "fake_private_key"}
    }

    mock_state_table.query.return_value = {"Count": 1}

    def mock_dynamo_table(table_name: str):
        if table_name == PATCH_ENV_VAR["AUTH_STATE_TABLE_NAME"]:
            return mock_state_table
        elif table_name == PATCH_ENV_VAR["AUTH_SESSION_TABLE_NAME"]:
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
    mocked_ods_api_call = mocker.patch.object(
        OdsApiService, "fetch_organisation_with_permitted_role"
    )
    mocked_ods_api_call.return_value = [
        {"org_name": "PORTWAY LIFESTYLE CENTRE", "ods_code": "A9A5A", "role": "DEV"}
    ]
    yield mocked_ods_api_call


@pytest.fixture
def mock_jwt(mocker):
    mocker.patch("jwt.encode", return_value="fake_auth_token")
    yield


def test_lambda_handler_respond_with_200_and_org_info_and_auth_token(
    patch_env_vars, mock_aws_infras, mock_oidc_service, mock_ods_api_service, mock_jwt
):
    test_event = {
        "queryStringParameters": {"code": "fake_auth_code", "state": "fake_state"}
    }

    expected_response_body = {
        "organisations": [
            {"org_name": "PORTWAY LIFESTYLE CENTRE", "ods_code": "A9A5A", "role": "DEV"}
        ],
        "authorisation_token": "fake_auth_token",
    }
    expected = ApiGatewayResponse(
        200, json.dumps(expected_response_body), "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(test_event, None)

    assert actual == expected


def test_lambda_handler_respond_with_400_if_state_or_auth_code_missing():
    expected = ApiGatewayResponse(
        400, "Please supply an authorisation code and state", "GET"
    ).create_api_gateway_response()

    missing_state = lambda_handler(
        {"queryStringParameters": {"code": "auth_code"}}, None
    )
    missing_auth_code = lambda_handler(
        {"queryStringParameters": {"state": "state"}}, None
    )
    missing_both = lambda_handler({"queryStringParameters": {}}, None)

    for actual in [missing_state, missing_auth_code, missing_both]:
        assert actual == expected


def test_lambda_handler_respond_with_401_when_auth_code_is_invalid(
    patch_env_vars, mock_aws_infras, mock_oidc_service, mock_ods_api_service, mock_jwt
):
    mock_oidc_service["fetch_token"].clear_mock()
    mock_oidc_service["fetch_token"].side_effect = AuthorisationException

    test_event = {
        "queryStringParameters": {"code": "invalid_token", "state": "fake_state"}
    }

    expected = ApiGatewayResponse(
        401, "Failed to authenticate user with OIDC service", "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(test_event, None)

    assert actual == expected
