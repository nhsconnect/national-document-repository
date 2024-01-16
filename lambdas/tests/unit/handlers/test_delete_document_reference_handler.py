import pytest
from botocore.exceptions import ClientError
from handlers.delete_document_reference_handler import lambda_handler
from services.document_deletion_service import DocumentDeletionService
from tests.unit.helpers.data.test_documents import (
    create_test_doc_store_refs,
    create_test_lloyd_george_doc_store_refs,
)
from utils.lambda_exceptions import DocumentDeletionServiceException
from utils.lambda_response import ApiGatewayResponse

TEST_DOC_STORE_REFERENCES = create_test_doc_store_refs()
TEST_LG_DOC_STORE_REFERENCES = create_test_lloyd_george_doc_store_refs()


@pytest.mark.parametrize(
    "event_body",
    [
        {
            "httpMethod": "GET",
            "queryStringParameters": {"patientId": "9000000009", "docType": "LG,ARF"},
        },
        {
            "httpMethod": "GET",
            "queryStringParameters": {"patientId": "9000000009", "docType": "ARF,LG"},
        },
        {
            "httpMethod": "GET",
            "queryStringParameters": {"patientId": "9000000009", "docType": "LG , ARF"},
        },
        {
            "httpMethod": "GET",
            "queryStringParameters": {"patientId": "9000000009", "docType": "ARF, LG"},
        },
    ],
)
def test_lambda_handler_valid_both_doc_types_successful_delete_returns_200(
    set_env, event_body, context, mock_handle_delete
):
    mock_handle_delete.return_value = (
        TEST_DOC_STORE_REFERENCES + TEST_LG_DOC_STORE_REFERENCES
    )

    expected = ApiGatewayResponse(
        200, "Success", "DELETE"
    ).create_api_gateway_response()

    actual = lambda_handler(event_body, context)

    assert expected == actual


def test_lambda_handler_valid_both_doc_types_empty_arf_doc_refs_successful_delete_returns_200(
    set_env, valid_id_and_both_doctype_event, context, mock_handle_delete
):
    mock_handle_delete.return_value = TEST_LG_DOC_STORE_REFERENCES

    expected = ApiGatewayResponse(
        200, "Success", "DELETE"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_and_both_doctype_event, context)

    assert expected == actual


def test_lambda_handler_valid_arf_docs_successful_delete_returns_200(
    mocker, set_env, valid_id_and_arf_doctype_event, context, mock_handle_delete
):
    mock_handle_delete.return_value = TEST_DOC_STORE_REFERENCES

    expected = ApiGatewayResponse(
        200, "Success", "DELETE"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_and_arf_doctype_event, context)

    assert expected == actual


def test_lambda_handler_valid_lg_docs_successful_delete_returns_200(
    set_env, valid_id_and_lg_doctype_event, context, mock_handle_delete
):
    mock_handle_delete.return_value = TEST_LG_DOC_STORE_REFERENCES

    expected = ApiGatewayResponse(
        200, "Success", "DELETE"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_and_lg_doctype_event, context)

    assert expected == actual


def test_lambda_handler_valid_both_doc_type_no_documents_found_returns_404(
    set_env, valid_id_and_both_doctype_event, context, mock_handle_delete
):
    mock_handle_delete.return_value = []

    expected = ApiGatewayResponse(
        404, "No documents available", "DELETE"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_and_both_doctype_event, context)

    assert expected == actual


def test_lambda_handler_no_documents_found_returns_404(
    set_env, valid_id_and_arf_doctype_event, context, mock_handle_delete
):
    mock_handle_delete.return_value = []

    expected = ApiGatewayResponse(
        404, "No documents available", "DELETE"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_and_arf_doctype_event, context)

    assert expected == actual


def test_lambda_handler_id_not_valid_returns_400(set_env, invalid_id_event, context):
    expected = ApiGatewayResponse(
        400, "Invalid NHS number", "GET"
    ).create_api_gateway_response()
    actual = lambda_handler(invalid_id_event, context)
    assert expected == actual


def test_lambda_handler_when_id_not_supplied_returns_400(
    set_env, missing_id_event, context
):
    expected = ApiGatewayResponse(
        400, "An error occurred due to missing key: 'patientId'", "GET"
    ).create_api_gateway_response()
    actual = lambda_handler(missing_id_event, context)
    assert expected == actual


def test_lambda_handler_returns_400_when_doc_type_not_supplied(
    set_env, valid_id_event_without_auth_header, context
):
    expected = ApiGatewayResponse(
        400, "An error occurred due to missing key: 'docType'", "GET"
    ).create_api_gateway_response()
    actual = lambda_handler(valid_id_event_without_auth_header, context)
    assert expected == actual


def test_lambda_handler_missing_environment_variables_returns_500(
    set_env, monkeypatch, valid_id_and_arf_doctype_event, context
):
    monkeypatch.delenv("DOCUMENT_STORE_DYNAMODB_NAME")
    expected = ApiGatewayResponse(
        500,
        "An error occurred due to missing environment variable: 'DOCUMENT_STORE_DYNAMODB_NAME'",
        "GET",
    ).create_api_gateway_response()
    actual = lambda_handler(valid_id_and_arf_doctype_event, context)
    assert expected == actual


def test_lambda_handler_when_deletion_service_throw_client_error_return_500(
    set_env, valid_id_and_arf_doctype_event, context, mock_handle_delete
):
    mock_error = ClientError(
        {"Error": {"Code": "403", "Message": "Forbidden"}},
        "S3:PutObjectTagging",
    )
    mock_handle_delete.side_effect = mock_error
    expected = ApiGatewayResponse(
        500, "Failed to utilise AWS client/resource", "GET", "GWY_5001"
    ).create_api_gateway_response()
    actual = lambda_handler(valid_id_and_arf_doctype_event, context)
    assert expected == actual


def test_lambda_handler_handle_lambda_exception(
    set_env, valid_id_and_lg_doctype_delete_event, context, mock_handle_delete
):
    mock_error = DocumentDeletionServiceException(
        status_code=404, err_code="DDS_XXXX", message="Mock error message"
    )
    mock_handle_delete.side_effect = mock_error
    expected = ApiGatewayResponse(
        404, "Mock error message", "DELETE", "DDS_XXXX"
    ).create_api_gateway_response()
    actual = lambda_handler(valid_id_and_lg_doctype_delete_event, context)
    assert expected == actual


@pytest.fixture
def mock_handle_delete(mocker):
    yield mocker.patch.object(DocumentDeletionService, "handle_delete")
