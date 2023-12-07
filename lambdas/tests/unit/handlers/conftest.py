import pytest


@pytest.fixture
def valid_id_event_without_auth_header():
    api_gateway_proxy_event = {
        "httpMethod": "GET",
        "queryStringParameters": {"patientId": "9000000009"},
        "headers": {},
    }
    return api_gateway_proxy_event


@pytest.fixture
def valid_id_event_with_auth_header():
    api_gateway_proxy_event = {
        "httpMethod": "GET",
        "queryStringParameters": {"patientId": "9000000009"},
        "headers": {"Authorization": "mock_token"},
    }
    return api_gateway_proxy_event


@pytest.fixture
def valid_id_and_both_doctype_event():
    api_gateway_proxy_event = {
        "httpMethod": "GET",
        "queryStringParameters": {"patientId": "9000000009", "docType": "LG,ARF"},
    }
    return api_gateway_proxy_event


@pytest.fixture
def valid_id_and_arf_doctype_event():
    api_gateway_proxy_event = {
        "httpMethod": "GET",
        "queryStringParameters": {"patientId": "9000000009", "docType": "ARF"},
    }
    return api_gateway_proxy_event


@pytest.fixture
def valid_id_and_lg_doctype_event():
    api_gateway_proxy_event = {
        "httpMethod": "GET",
        "queryStringParameters": {"patientId": "9000000009", "docType": "LG"},
    }
    return api_gateway_proxy_event


@pytest.fixture
def valid_id_and_lg_doctype_delete_event():
    api_gateway_proxy_event = {
        "httpMethod": "DELETE",
        "queryStringParameters": {"patientId": "9000000009", "docType": "LG"},
    }
    return api_gateway_proxy_event


@pytest.fixture
def valid_id_and_invalid_doctype_event():
    api_gateway_proxy_event = {
        "httpMethod": "GET",
        "queryStringParameters": {"patientId": "9000000009", "docType": "MANGO"},
    }
    return api_gateway_proxy_event


@pytest.fixture
def invalid_id_event():
    api_gateway_proxy_event = {
        "httpMethod": "GET",
        "queryStringParameters": {"patientId": "900000000900"},
    }
    return api_gateway_proxy_event


@pytest.fixture
def missing_id_event():
    api_gateway_proxy_event = {
        "httpMethod": "GET",
        "queryStringParameters": {"invalid": ""},
    }
    return api_gateway_proxy_event
