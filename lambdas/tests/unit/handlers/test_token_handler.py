import json

import pytest
from enums.repository_role import RepositoryRole
from handlers.token_handler import lambda_handler
from utils.lambda_exceptions import LoginException
from utils.lambda_response import ApiGatewayResponse


@pytest.fixture
def mock_login_service(mocker, set_env):
    mock_service = mocker.patch("handlers.token_handler.LoginService")
    yield mock_service.return_value


def test_lambda_handler_respond_with_200_including_org_info_and_auth_token(
    mock_login_service,
    context,
):
    expected_jwt = "mock_ndr_auth_token"
    login_service_response = {
        "isBSOL": False,
        "role": RepositoryRole.PCSE.value,
        "authorisation_token": expected_jwt,
    }
    mock_login_service.generate_session.return_value = login_service_response

    auth_code = "auth_code"
    state = "test_state"
    test_event = {
        "queryStringParameters": {"code": auth_code, "state": state},
        "httpmethod": "GET",
    }

    expected_response_body = {
        "isBSOL": False,
        "role": "PCSE",
        "authorisation_token": expected_jwt,
    }

    expected = ApiGatewayResponse(
        200, json.dumps(expected_response_body), "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(test_event, context)

    assert actual == expected

    mock_login_service.generate_session.assert_called_with(state, auth_code)


def test_handler_passes_error_details_in_response(
    mock_login_service,
    context,
):
    expected_status = 400
    expected_body = "Error desc"
    exception = LoginException(status_code=expected_status, message=expected_body)
    mock_login_service.generate_session.side_effect = exception

    auth_code = "auth_code"
    state = "test_state"
    test_event = {
        "queryStringParameters": {"code": auth_code, "state": state},
        "httpmethod": "GET",
    }

    expected = ApiGatewayResponse(
        expected_status, expected_body, "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(test_event, context)

    assert actual == expected

    mock_login_service.generate_session.assert_called_with(state, auth_code)


def test_missing_query_string_params_raise_key_error(mock_login_service, context):
    expected_status = 400
    expected_body = "No auth code and/or state in the query string parameters"

    auth_code = "auth_code"
    test_event = {
        "queryStringParameters": {"test": auth_code},
        "httpmethod": "GET",
    }

    expected = ApiGatewayResponse(
        expected_status, expected_body, "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(test_event, context)

    assert actual == expected

    mock_login_service.generate_session.assert_not_called()


def test_missing_query_string_params_raise_login_error(
    mock_login_service,
    context,
):
    expected_status = 400
    expected_body = "No auth code and/or state in the query string parameters"

    test_event = {
        "queryStringParameters": {"code": "", "state": ""},
        "httpmethod": "GET",
    }
    expected = ApiGatewayResponse(
        expected_status, expected_body, "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(test_event, context)

    assert actual == expected
    mock_login_service.generate_session.assert_not_called()
