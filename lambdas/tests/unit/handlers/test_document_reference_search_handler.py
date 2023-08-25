from dataclasses import dataclass

import pytest

from handlers.document_reference_search_handler import lambda_handler
from utils.lambda_response import ApiGatewayResponse


@pytest.fixture
def valid_nhs_id_event():
    api_gateway_proxy_event = {
        "queryStringParameters": {"patientId": "9000000009"},
    }
    return api_gateway_proxy_event


@pytest.fixture
def context():
    @dataclass
    class LambdaContext:
        function_name: str = "test"
        aws_request_id: str = "88888888-4444-4444-4444-121212121212"
        invoked_function_arn: str = (
            "arn:aws:lambda:eu-west-1:123456789101:function:test"
        )

    return LambdaContext()


def test_lambda_handler_returns_200(valid_nhs_id_event, context):
    expected = ApiGatewayResponse(200, "OK", "GET")
    actual = lambda_handler(valid_nhs_id_event, context)

    assert actual == expected

