from unittest.mock import MagicMock

import pytest
from enums.metadata_field_names import DocumentReferenceMetadataFields
from handlers.document_manifest_by_nhs_number_handler import (lambda_handler,
                                                              query_documents)
from services.dynamo_service import DynamoDBService
from tests.unit.helpers.data.dynamo_responses import \
    MOCK_MANIFEST_QUERY_RESPONSE
from tests.unit.helpers.data.test_documents import TEST_DS_DOCS, TEST_LG_DOCS
from utils.lambda_response import ApiGatewayResponse

MOCK_TABLE = "test-table"
NHS_NUMBER = "1111111111"

TEST_METADATA_FIELDS = [
    DocumentReferenceMetadataFields.FILE_NAME,
    DocumentReferenceMetadataFields.FILE_LOCATION,
    DocumentReferenceMetadataFields.VIRUS_SCAN_RESULT,
]


@pytest.fixture
def mock_dynamo_service():
    return MagicMock()


def test_lambda_handler_returns_204_when_no_documents_returned_from_dynamo_response(
    mocker, set_env, valid_id_event, context
):
    mock_lg_docs = mocker.patch(
        "handlers.document_manifest_by_nhs_number_handler.get_lloyd_george_documents"
    )
    mock_lg_docs.return_value = []

    mock_ds_docs = mocker.patch(
        "handlers.document_manifest_by_nhs_number_handler.get_doc_store_documents"
    )
    mock_ds_docs.return_value = []

    expected = ApiGatewayResponse(
        204, "No documents found for given NHS number", "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_event, context)

    assert expected == actual


def test_lambda_handler_valid_parameters_returns_200(
    mocker, set_env, valid_id_event, context
):
    expected_url = "test-url"

    mock_lg_docs = mocker.patch(
        "handlers.document_manifest_by_nhs_number_handler.get_lloyd_george_documents"
    )
    mock_lg_docs.return_value = TEST_LG_DOCS

    mock_ds_docs = mocker.patch(
        "handlers.document_manifest_by_nhs_number_handler.get_doc_store_documents"
    )
    mock_ds_docs.return_value = TEST_DS_DOCS

    mock_doc_manifest_url = mocker.patch(
        "services.document_manifest_service.DocumentManifestService.create_document_manifest_presigned_url"
    )
    mock_doc_manifest_url.return_value = expected_url

    expected = ApiGatewayResponse(
        200, expected_url, "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_event, context)

    assert expected == actual


def test_lambda_handler_missing_environment_variables_returns_400(
    set_env, monkeypatch, valid_id_event, context
):
    monkeypatch.delenv("DOCUMENT_STORE_DYNAMODB_NAME")
    expected = ApiGatewayResponse(
        400,
        "An error occurred due to missing key: 'DOCUMENT_STORE_DYNAMODB_NAME'",
        "GET",
    ).create_api_gateway_response()
    actual = lambda_handler(valid_id_event, context)
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


def test_query_documents(set_env, mocker):
    mock_dynamo_service = DynamoDBService()

    query_patch = mocker.patch("services.dynamo_service.DynamoDBService.query_service")
    query_patch.return_value = MOCK_MANIFEST_QUERY_RESPONSE

    expected = TEST_DS_DOCS

    response = query_documents(mock_dynamo_service, NHS_NUMBER)

    assert response == expected
