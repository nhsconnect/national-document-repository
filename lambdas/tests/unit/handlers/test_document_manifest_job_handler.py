import json
from enum import Enum

import pytest
from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from enums.metadata_field_names import DocumentReferenceMetadataFields
from enums.supported_document_types import SupportedDocumentTypes
from handlers.document_manifest_job_handler import create_manifest_job, lambda_handler
from tests.unit.conftest import TEST_NHS_NUMBER, TEST_UUID
from utils.lambda_exceptions import DocumentManifestJobServiceException
from utils.lambda_response import ApiGatewayResponse

TEST_METADATA_FIELDS = [
    DocumentReferenceMetadataFields.FILE_NAME,
    DocumentReferenceMetadataFields.FILE_LOCATION,
    DocumentReferenceMetadataFields.VIRUS_SCANNER_RESULT,
]


class MockError(Enum):
    Error = {
        "message": "Client error",
        "err_code": "AB_XXXX",
        "interaction_id": "88888888-4444-4444-4444-121212121212",
    }


@pytest.fixture
def valid_id_and_both_doctype_post_event():
    api_gateway_proxy_event = {
        "httpMethod": "POST",
        "queryStringParameters": {"patientId": TEST_NHS_NUMBER, "docType": "LG,ARF"},
        "multiValueQueryStringParameters": {},
    }
    return api_gateway_proxy_event


@pytest.fixture
def valid_id_and_arf_doctype_post_event():
    api_gateway_proxy_event = {
        "httpMethod": "POST",
        "queryStringParameters": {"patientId": TEST_NHS_NUMBER, "docType": "ARF"},
        "multiValueQueryStringParameters": {},
    }
    return api_gateway_proxy_event


@pytest.fixture
def valid_id_and_lg_doctype_post_event():
    api_gateway_proxy_event = {
        "httpMethod": "POST",
        "queryStringParameters": {"patientId": TEST_NHS_NUMBER, "docType": "LG"},
        "multiValueQueryStringParameters": {},
    }
    return api_gateway_proxy_event


@pytest.fixture
def valid_id_and_invalid_doctype_post_event():
    api_gateway_proxy_event = {
        "httpMethod": "POST",
        "queryStringParameters": {"patientId": TEST_NHS_NUMBER, "docType": "MANGO"},
        "multiValueQueryStringParameters": {},
    }
    return api_gateway_proxy_event


@pytest.fixture
def valid_id_and_lg_doctype_post_event_with_doc_references():
    api_gateway_proxy_event = {
        "httpMethod": "POST",
        "queryStringParameters": {
            "patientId": TEST_NHS_NUMBER,
            "docType": "LG",
        },
        "multiValueQueryStringParameters": {
            "docReferences": ["test-doc-ref", "test-doc-ref2"],
        },
    }
    return api_gateway_proxy_event


@pytest.fixture
def valid_job_id_get_event():
    api_gateway_proxy_event = {
        "httpMethod": "GET",
        "queryStringParameters": {
            "jobId": TEST_UUID,
        },
    }
    return api_gateway_proxy_event


@pytest.fixture
def mock_manifest_service(set_env, mocker):
    mocked_class = mocker.patch(
        "handlers.document_manifest_job_handler.DocumentManifestJobService"
    )
    mocked_service = mocked_class.return_value
    yield mocked_service


@pytest.fixture
def mock_create_manifest_job(set_env, mocker):
    yield mocker.patch("handlers.document_manifest_job_handler.create_manifest_job")


@pytest.fixture
def mock_get_manifest_job(set_env, mocker):
    yield mocker.patch("handlers.document_manifest_job_handler.get_manifest_job")


def test_lambda_handler_calls_correct_method_handler_for_post(
    mock_create_manifest_job, valid_id_and_arf_doctype_post_event, context
):
    mock_create_manifest_job.return_value = ApiGatewayResponse(
        200, json.dumps(TEST_UUID), "POST"
    ).create_api_gateway_response()

    expected = ApiGatewayResponse(
        200, json.dumps(TEST_UUID), "POST"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_and_arf_doctype_post_event, context)

    mock_create_manifest_job.assert_called_once_with(
        valid_id_and_arf_doctype_post_event, context
    )
    assert expected == actual


def test_lambda_handler_calls_correct_method_handler_for_get(
    mock_get_manifest_job, valid_job_id_get_event, context
):
    test_response = {"jobStatus": "Pending", "url": "test-url.com"}
    mock_get_manifest_job.return_value = ApiGatewayResponse(
        200, json.dumps(test_response), "GET"
    ).create_api_gateway_response()

    expected = ApiGatewayResponse(
        200, json.dumps(test_response), "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_job_id_get_event, context)

    mock_get_manifest_job.assert_called_once_with(valid_job_id_get_event, context)
    assert expected == actual


def test_create_manifest_job_valid_parameters_arf_doc_type_post_request_returns_200(
    mock_manifest_service, valid_id_and_arf_doctype_post_event, context
):
    mock_manifest_service.create_document_manifest_job.return_value = TEST_UUID

    expected_job_id = {"jobId": TEST_UUID}

    expected = ApiGatewayResponse(
        200, json.dumps(expected_job_id), "POST"
    ).create_api_gateway_response()

    actual = create_manifest_job(valid_id_and_arf_doctype_post_event, context)

    mock_manifest_service.create_document_manifest_job.assert_called_once_with(
        TEST_NHS_NUMBER, [SupportedDocumentTypes.ARF], None
    )
    assert expected == actual


def test_create_manifest_job_valid_parameters_lg_doc_type_post_request_returns_200(
    mock_manifest_service, valid_id_and_lg_doctype_post_event, context
):
    mock_manifest_service.create_document_manifest_job.return_value = TEST_UUID

    expected_job_id = {"jobId": TEST_UUID}

    expected = ApiGatewayResponse(
        200, json.dumps(expected_job_id), "POST"
    ).create_api_gateway_response()

    actual = create_manifest_job(valid_id_and_lg_doctype_post_event, context)

    mock_manifest_service.create_document_manifest_job.assert_called_once_with(
        TEST_NHS_NUMBER, [SupportedDocumentTypes.LG], None
    )
    assert expected == actual


def test_create_manifest_job_valid_parameters_both_doc_type_post_request_returns_200(
    mock_manifest_service, valid_id_and_both_doctype_post_event, context
):
    mock_manifest_service.create_document_manifest_job.return_value = TEST_UUID

    expected_job_id = {"jobId": TEST_UUID}

    expected = ApiGatewayResponse(
        200, json.dumps(expected_job_id), "POST"
    ).create_api_gateway_response()

    actual = create_manifest_job(valid_id_and_both_doctype_post_event, context)

    mock_manifest_service.create_document_manifest_job.assert_called_once_with(
        TEST_NHS_NUMBER, [SupportedDocumentTypes.LG, SupportedDocumentTypes.ARF], None
    )
    assert expected == actual


def test_lambda_handler_sets_document_references_when_event_contains_document_reference_params(
    mock_manifest_service,
    valid_id_and_lg_doctype_post_event_with_doc_references,
    context,
):
    mock_manifest_service.create_document_manifest_job.return_value = TEST_UUID

    expected_job_id = {"jobId": TEST_UUID}

    expected = ApiGatewayResponse(
        200, json.dumps(expected_job_id), "POST"
    ).create_api_gateway_response()

    actual = create_manifest_job(
        valid_id_and_lg_doctype_post_event_with_doc_references, context
    )

    mock_manifest_service.create_document_manifest_job.assert_called_once_with(
        TEST_NHS_NUMBER, [SupportedDocumentTypes.LG], ["test-doc-ref", "test-doc-ref2"]
    )
    assert expected == actual


def test_lambda_handler_when_service_raises_client_error_returns_correct_response(
    mock_manifest_service, valid_id_and_arf_doctype_post_event, context
):
    expected_body = json.dumps(
        {
            "message": "Failed to utilise AWS client/resource",
            "err_code": "GWY_5001",
            "interaction_id": "88888888-4444-4444-4444-121212121212",
        }
    )
    exception = ClientError({}, "test")
    mock_manifest_service.create_document_manifest_job.side_effect = exception

    expected = ApiGatewayResponse(
        500,
        expected_body,
        "POST",
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_and_arf_doctype_post_event, context)

    assert expected == actual


def test_lambda_handler_when_service_raises_document_manifest_exception_returns_correct_response(
    mock_manifest_service, valid_id_and_arf_doctype_post_event, context
):
    exception = DocumentManifestJobServiceException(
        status_code=404, error=LambdaError.MockError
    )
    mock_manifest_service.create_document_manifest_job.side_effect = exception

    expected = ApiGatewayResponse(
        404,
        json.dumps(MockError.Error.value),
        "POST",
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_and_arf_doctype_post_event, context)

    assert expected == actual


def test_lambda_handler_when_doc_type_invalid_returns_400(
    mock_manifest_service, valid_id_and_invalid_doctype_post_event, context
):
    expected_body = json.dumps(
        {
            "message": "Invalid document type requested",
            "err_code": "VDT_4002",
            "interaction_id": "88888888-4444-4444-4444-121212121212",
        }
    )
    expected = ApiGatewayResponse(
        400, expected_body, "POST"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_and_invalid_doctype_post_event, context)

    assert expected == actual


def test_lambda_handler_missing_environment_variables_returns_500(
    set_env, monkeypatch, valid_id_and_arf_doctype_post_event, context
):
    monkeypatch.delenv("DOCUMENT_STORE_DYNAMODB_NAME")

    expected_body = json.dumps(
        {
            "message": "An error occurred due to missing environment variable: 'DOCUMENT_STORE_DYNAMODB_NAME'",
            "err_code": "ENV_5001",
            "interaction_id": "88888888-4444-4444-4444-121212121212",
        }
    )
    expected = ApiGatewayResponse(
        500,
        expected_body,
        "POST",
    ).create_api_gateway_response()
    actual = lambda_handler(valid_id_and_arf_doctype_post_event, context)
    assert expected == actual


def test_lambda_handler_id_not_valid_returns_400(set_env, invalid_id_event, context):
    invalid_id_event["httpMethod"] = "POST"
    expected_body = json.dumps(
        {
            "message": "Invalid patient number 900000000900",
            "err_code": "PN_4001",
            "interaction_id": "88888888-4444-4444-4444-121212121212",
        }
    )
    expected = ApiGatewayResponse(
        400, expected_body, "POST"
    ).create_api_gateway_response()
    actual = lambda_handler(invalid_id_event, context)
    assert expected == actual


def test_lambda_handler_when_id_not_supplied_returns_400(
    set_env, missing_id_event, context
):
    missing_id_event["httpMethod"] = "POST"
    missing_id_event["queryStringParameters"]["docType"] = "test"

    expected_body = json.dumps(
        {
            "message": "An error occurred due to missing key",
            "err_code": "PN_4002",
            "interaction_id": "88888888-4444-4444-4444-121212121212",
        }
    )
    expected = ApiGatewayResponse(
        400, expected_body, "POST"
    ).create_api_gateway_response()
    actual = lambda_handler(missing_id_event, context)
    assert expected == actual


def test_lambda_handler_returns_400_when_doc_type_not_supplied(
    set_env, valid_id_event_without_auth_header, context
):
    expected_body = json.dumps(
        {
            "message": "An error occurred due to missing key",
            "err_code": "VDT_4003",
            "interaction_id": "88888888-4444-4444-4444-121212121212",
        }
    )
    expected = ApiGatewayResponse(
        400, expected_body, "GET"
    ).create_api_gateway_response()
    actual = lambda_handler(valid_id_event_without_auth_header, context)
    assert expected == actual
