from handlers.delete_document_reference_handler import lambda_handler
from tests.unit.helpers.data.test_documents import (
    create_test_doc_store_refs, create_test_lloyd_george_doc_store_refs)
from utils.lambda_response import ApiGatewayResponse

TEST_DOC_STORE_REFERENCES = create_test_doc_store_refs()
TEST_LG_DOC_STORE_REFERENCES = create_test_lloyd_george_doc_store_refs()


def test_lambda_handler_valid_arf_docs_successful_delete_returns_204(
    mocker, set_env, valid_id_and_arf_doctype_event, context
):
    mock_document_query = mocker.patch(
        "services.document_service.DocumentService.fetch_documents_from_table"
    )
    mock_document_query.return_value = TEST_DOC_STORE_REFERENCES

    mocker.patch("services.document_service.DocumentService.delete_documents")

    expected = ApiGatewayResponse(
        204, "Successfully deleted documents", "DELETE"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_and_arf_doctype_event, context)

    assert expected == actual


def test_lambda_handler_valid_lg_docs_successful_delete_returns_204(
    mocker, set_env, valid_id_and_lg_doctype_event, context
):
    mock_document_query = mocker.patch(
        "services.document_service.DocumentService.fetch_documents_from_table"
    )
    mock_document_query.return_value = TEST_LG_DOC_STORE_REFERENCES

    mocker.patch("services.document_service.DocumentService.delete_documents")

    expected = ApiGatewayResponse(
        204, "Successfully deleted documents", "DELETE"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_and_lg_doctype_event, context)

    assert expected == actual


def test_lambda_handler_no_documents_found_returns_404(
    mocker, set_env, valid_id_and_arf_doctype_event, context
):
    mock_document_query = mocker.patch(
        "services.document_service.DocumentService.fetch_documents_from_table"
    )
    mock_document_query.return_value = []

    mocker.patch("services.document_service.DocumentService.delete_documents")

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
    set_env, valid_id_event, context
):
    expected = ApiGatewayResponse(
        400, "An error occurred due to missing key: 'docType'", "GET"
    ).create_api_gateway_response()
    actual = lambda_handler(valid_id_event, context)
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
