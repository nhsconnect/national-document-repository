import json

import pytest
from handlers.access_audit_handler import lambda_handler
from utils.lambda_response import ApiGatewayResponse


@pytest.fixture
def mock_service(mocker):
    mock_service = mocker.MagicMock()
    mocker.patch(
        "handlers.access_audit_handler.AccessAuditService",
        return_value=mock_service,
    )
    yield mock_service


def test_lambda_handler_success(set_env, context, mock_service):
    event = {
        "httpMethod": "POST",
        "queryStringParameters": {"patientId": "0123456789", "accessAuditType": "view"},
        "body": json.dumps({"someKey": "someValue"}),
    }
    response = lambda_handler(event, context)
    expected = ApiGatewayResponse(
        200,
        "",
        "POST",
    ).create_api_gateway_response()
    assert expected == response


def test_lambda_handler_missing_parameters(set_env, context, mock_service):
    event = {
        "httpMethod": "POST",
        "queryStringParameters": {
            "patientId": "0123456789",
        },
        "body": json.dumps({"someKey": "someValue"}),
    }
    expected_body = {
        "message": "Invalid reason code",
        "err_code": "AA_4001",
        "interaction_id": "88888888-4444-4444-4444-121212121212",
    }
    response = lambda_handler(event, context)
    expected = ApiGatewayResponse(
        400,
        json.dumps(expected_body),
        "POST",
    ).create_api_gateway_response()
    assert expected == response
