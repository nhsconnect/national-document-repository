from unittest.mock import call

from enums.metadata_field_names import DocumentReferenceMetadataFields
from enums.supported_document_types import SupportedDocumentTypes
from handlers.document_manifest_by_nhs_number_handler import lambda_handler
from tests.unit.helpers.data.test_documents import (
    create_test_doc_store_refs, create_test_lloyd_george_doc_store_refs)
from utils.lambda_response import ApiGatewayResponse

TEST_METADATA_FIELDS = [
    DocumentReferenceMetadataFields.FILE_NAME,
    DocumentReferenceMetadataFields.FILE_LOCATION,
    DocumentReferenceMetadataFields.VIRUS_SCANNER_RESULT,
]


def test_lambda_handler_returns_204_when_no_documents_returned_from_dynamo_response(
    mocker, set_env, valid_id_and_arf_doctype_event, context
):
    mock_document_query = mocker.patch(
        "services.document_service.DocumentService.fetch_available_document_references_by_type"
    )
    mock_document_query.return_value = []

    expected = ApiGatewayResponse(
        204, "No documents found for given NHS number and document type", "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_and_arf_doctype_event, context)

    assert expected == actual


def test_lambda_handler_returns_400_when_doc_type_invalid_response(
    mocker, set_env, valid_id_and_invalid_doctype_event, context
):
    mock_document_query = mocker.patch(
        "services.document_service.DocumentService.fetch_available_document_references_by_type"
    )
    mock_document_query.return_value = []

    expected = ApiGatewayResponse(
        400, "Invalid document type requested", "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_and_invalid_doctype_event, context)

    assert expected == actual


def manifest_service_side_effect(nhs_number, doc_type):
    if doc_type == SupportedDocumentTypes.ARF.value:
        return create_test_doc_store_refs()
    if doc_type == SupportedDocumentTypes.LG.value:
        return create_test_lloyd_george_doc_store_refs()
    if doc_type == SupportedDocumentTypes.ALL.value:
        return create_test_doc_store_refs() + create_test_lloyd_george_doc_store_refs()
    return []


def test_lambda_handler_valid_parameters_arf_doc_type_request_returns_200(
    mocker, set_env, valid_id_and_arf_doctype_event, context
):
    expected_url = "test-url"

    mock_document_query = mocker.patch(
        "services.document_service.DocumentService.fetch_available_document_references_by_type"
    )
    mock_document_query.side_effect = manifest_service_side_effect

    mock_doc_manifest_url = mocker.patch(
        "services.document_manifest_service.DocumentManifestService.create_document_manifest_presigned_url"
    )
    mock_doc_manifest_url.return_value = expected_url

    expected = ApiGatewayResponse(
        200, expected_url, "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_and_arf_doctype_event, context)
    mock_document_query.assert_called_once_with("9000000009", "ARF")
    assert expected == actual


def test_lambda_handler_valid_parameters_lg_doc_type_request_returns_200(
    mocker, set_env, valid_id_and_lg_doctype_event, context
):
    expected_url = "test-url"

    mock_document_query = mocker.patch(
        "services.document_service.DocumentService.fetch_available_document_references_by_type"
    )
    mock_document_query.side_effect = manifest_service_side_effect

    mock_doc_manifest_url = mocker.patch(
        "services.document_manifest_service.DocumentManifestService.create_document_manifest_presigned_url"
    )
    mock_doc_manifest_url.return_value = expected_url

    expected = ApiGatewayResponse(
        200, expected_url, "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_and_lg_doctype_event, context)
    mock_document_query.assert_called_once_with("9000000009", "LG")
    assert expected == actual


def test_lambda_handler_valid_parameters_both_doc_type_request_returns_200(
    mocker, set_env, valid_id_and_both_doctype_event, context
):
    expected_url = "test-url"

    mock_document_query = mocker.patch(
        "services.document_service.DocumentService.fetch_available_document_references_by_type"
    )
    mock_document_query.side_effect = manifest_service_side_effect

    mock_doc_manifest_url = mocker.patch(
        "services.document_manifest_service.DocumentManifestService.create_document_manifest_presigned_url"
    )
    mock_doc_manifest_url.return_value = expected_url

    expected = ApiGatewayResponse(
        200, expected_url, "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_and_both_doctype_event, context)
    mock_document_query.assert_has_calls(
        [
            call("9000000009", "ALL"),
        ]
    )
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
