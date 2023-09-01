from dataclasses import dataclass

import pytest


@pytest.fixture
def event_valid_id():
    api_gateway_proxy_event = {
        "queryStringParameters": {"patientId": "9000000009"},
    }
    return api_gateway_proxy_event


@pytest.fixture
def event_invalid_id():
    api_gateway_proxy_event = {
        "queryStringParameters": {"patientId": "900000000900"},
    }
    return api_gateway_proxy_event


@pytest.fixture
def invalid_nhs_id_event():
    api_gateway_proxy_event = {
        "queryStringParameters": {"patientId": "9000AB0009"},
    }
    return api_gateway_proxy_event


@pytest.fixture
def empty_nhs_id_event():
    api_gateway_proxy_event = {
        "queryStringParameters": {"inpatientId": "blah"},
    }
    return api_gateway_proxy_event


@pytest.fixture
def event_missing_id():
    api_gateway_proxy_event = {
        "queryStringParameters": {"invalid": "9000000009"},
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
