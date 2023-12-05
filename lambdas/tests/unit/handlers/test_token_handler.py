import json
import os
from unittest.mock import patch

import jwt
import pytest
from botocore.exceptions import ClientError
from enums.repository_role import RepositoryRole
from handlers.token_handler import lambda_handler
from services.login_service import LoginService
from services.oidc_service import OidcService
from utils.audit_logging_setup import LoggingService
from utils.exceptions import AuthorisationException
from utils.lambda_response import ApiGatewayResponse

@pytest.fixture
def mock_login_service(mocker):
    yield mocker.patch.object(LoginService, "__init__", return_value=None)


@pytest.fixture
def mock_logging_service(mocker):
    yield mocker.patch.object(LoggingService, "__init__", return_value=None)


def test_lambda_handler_respond_with_200_including_org_info_and_auth_token( #TODO injection of login service mock is broken :)
    set_env,
    mock_logging_service,
    mock_login_service,
    mocker,
    context,
):
    expected_jwt = "mock_ndr_auth_token"
    login_service_response = {"local_role": RepositoryRole.PCSE, "jwt": expected_jwt}
    mocker.patch.object(LoginService, "exchange_token", return_value=login_service_response)

    auth_code = "auth_code"
    state = "test_state"
    test_event = {
        "queryStringParameters": {"code": auth_code, "state": state},
        "httpmethod": "GET",
    }

    expected_response_body = {
        "role": "PCSE",
        "authorisation_token": expected_jwt,
    }

    expected = ApiGatewayResponse(
        200, json.dumps(expected_response_body), "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(test_event, context)

    assert actual == expected

    mock_login_service["exchange_token"].expect_called_with(auth_code, state)


#TODO Test errors including autherrors (return 401) and erroneous errors (e.g. encoding, keyerrors (return 500)