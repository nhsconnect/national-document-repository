import pytest


@pytest.fixture
def valid_id_event():
    api_gateway_proxy_event = {
        "httpMethod": "GET",
        "queryStringParameters": {"patientId": "9000000009", "jobId": "123456890"},
    }
    return api_gateway_proxy_event


@pytest.fixture
def missing_query_string_event():
    api_gateway_proxy_event = {
        "httpMethod": "GET",
    }
    return api_gateway_proxy_event


@pytest.fixture
def invalid_nhs_number_event():
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
def valid_id_and_both_doctype_event():
    api_gateway_proxy_event = {
        "httpMethod": "GET",
        "queryStringParameters": {"patientId": "9000000009", "docType": "LG,ARF"},
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
def valid_id_and_nonsense_doctype_event():
    api_gateway_proxy_event = {
        "httpMethod": "GET",
        "queryStringParameters": {
            "patientId": "9000000009",
            "docType": "sdfjfvsjhfvsukjARFfjdhtgdkjughLG",
        },
    }
    return api_gateway_proxy_event


@pytest.fixture
def valid_id_and_empty_doctype_event():
    api_gateway_proxy_event = {
        "httpMethod": "GET",
        "queryStringParameters": {"patientId": "9000000009", "docType": ""},
    }
    return api_gateway_proxy_event


@pytest.fixture
def valid_id_and_none_doctype_event():
    api_gateway_proxy_event = {
        "httpMethod": "GET",
        "queryStringParameters": {"patientId": "9000000009", "docType": None},
    }
    return api_gateway_proxy_event


@pytest.fixture
def error_override_env_vars(monkeypatch):
    monkeypatch.setenv("WORKSPACE", "ndra")
    monkeypatch.setenv("ERROR_TRIGGER", "400")
