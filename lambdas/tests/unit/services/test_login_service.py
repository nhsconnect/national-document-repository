import os
from unittest.mock import patch

import jwt
import pytest
from botocore.exceptions import ClientError
from enums.repository_role import RepositoryRole
from models.oidc_models import IdTokenClaimSet
from services.login_service import LoginService
from services.ods_api_service import OdsApiService
from services.oidc_service import OidcService
from utils.audit_logging_setup import LoggingService
from utils.exceptions import AuthorisationException


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


def test_exchange_token_respond_with_auth_token_and_repo_role(
    set_env,
    mock_aws_infras,
    mock_oidc_service,
    mock_ods_api_service,
    mock_jwt_encode,
    mock_logging_service,
    mocker,
    context,
):
    auth_code = "auth_code"
    state = "state"

    expected_jwt = "mock_ndr_auth_token"
    expected_role = RepositoryRole.PCSE

    mocker.patch(
        "services.login_service.create_login_session",
        return_value="new_item_session_id",
    )
    mocker.patch(
        "services.login_service.generate_repository_role",
        return_value=expected_role,
    )
    mocker.patch("services.login_service.issue_auth_token", return_value=expected_jwt)

    expected = {"local_role": RepositoryRole.PCSE, "JWT": expected_jwt}

    login_service = LoginService()

    actual = login_service.exchange_token(auth_code, state)

    assert actual == expected

    mock_oidc_service["fetch_token"].expect_called_with(auth_code)


def test_exchange_token_raises_auth_exception_when_auth_code_is_invalid(
    mock_aws_infras,
    mock_oidc_service,
    mock_ods_api_service,
    mock_jwt_encode,
    set_env,
    context,
):
    mock_oidc_service["fetch_token"].side_effect = AuthorisationException
    login_service = LoginService()

    with pytest.raises(AuthorisationException):
        login_service.exchange_token("auth_code", "state")
        # TODO assert 401 in error

    mock_oidc_service["fetch_user_org_codes"].assert_not_called()
    mock_aws_infras["session_table"].post.assert_not_called()


def test_exchange_token_raises_auth_error_when_given_state_is_not_in_state_table(
    mock_aws_infras, mock_oidc_service, set_env, context
):
    mock_aws_infras["state_table"].query.return_value = {"Count": 0, "Items": []}

    login_service = LoginService()

    with pytest.raises(AuthorisationException):
        login_service.exchange_token("auth_code", "state")
        # TODO assert 401 in error

    mock_oidc_service["fetch_token"].assert_not_called()
    mock_oidc_service["fetch_user_org_codes"].assert_not_called()
    mock_aws_infras["session_table"].post.assert_not_called()


def test_exchange_token_raises_auth_error_when_user_doesnt_have_a_valid_role_to_login(
    mock_aws_infras,
    mock_oidc_service,
    mocker,
):
    class PermittedOrgs:
        def keys(self):
            return []

    mocker.patch(
        "services.ods_api_service.OdsApiService.fetch_organisation_with_permitted_role"
    ).return_value = PermittedOrgs()

    login_service = LoginService()

    with pytest.raises(AuthorisationException):
        login_service.exchange_token("auth_code", "state")
        # TODO assert 401 in error

    mock_aws_infras["session_table"].post.assert_not_called()


# TODO needs to go in dynamo service tests when refactoring of CUT is done
def test_exchange_token_raises_error_when_encounter_boto3_error(
    mock_aws_infras, set_env, mocker, context
):
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

    login_service = LoginService()

    with pytest.raises(Exception):
        login_service.exchange_token("auth_code", "state")
    # TODO assert 500 in error


def test_exchange_token_raises_error_when_encounter_pyjwt_encode_error(
    mock_aws_infras,
    mock_oidc_service,
    mock_ods_api_service,
    mock_jwt_encode,
    set_env,
    context,
):
    jwt_error = jwt.PyJWTError()
    patch.object(OidcService, "fetch_tokens", side_effect=jwt_error)

    login_service = LoginService()

    with pytest.raises(Exception):
        login_service.exchange_token("auth_code", "state")

    # TODO assert 500 in error
