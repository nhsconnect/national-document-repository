import os
from unittest.mock import patch, MagicMock

import pytest

from conftest import PATCH_DYNAMO_TABLES_ENV_VAR
from enums.metadata_field_names import DynamoDocumentMetadataTableFields
from handlers.create_document_manifest_by_nhs_number_handler import lambda_handler, find_document_locations
from services.dynamo_query_service import DynamoQueryService
from helpers.dynamo_responses import LOCATION_QUERY_RESPONSE, MOCK_EMPTY_RESPONSE

from botocore.exceptions import ClientError
from utils.lambda_response import ApiGatewayResponse

NHS_NUMBER = 1111111111


@pytest.fixture
def mock_dynamo_service():
    return MagicMock()


def test_lambda_handler_returns_error_response_when_no_documents_returned_from_dynamo_response(mock_dynamo_service,
                                                                                               event_valid_id, context):
    expected = ApiGatewayResponse(204, "No documents found for given NHS number", "GET").create_api_gateway_response()
    with patch.object(DynamoQueryService, "__call__", new=mock_dynamo_service) as call_mock:
        call_mock.return_value = LOCATION_QUERY_RESPONSE
        actual = lambda_handler(event_valid_id, context)
        call_mock.assert_called_with("NhsNumber", "9000000009",
                                     [DynamoDocumentMetadataTableFields.LOCATION])
    assert expected == actual


def test_find_docs_returns_items_from_dynamo_response(mock_dynamo_service):
    with patch.object(DynamoQueryService, "__call__", new=mock_dynamo_service) as call_mock:
        call_mock.return_value = LOCATION_QUERY_RESPONSE
        actual = find_document_locations(NHS_NUMBER)
        call_mock.assert_called_with("NhsNumber", NHS_NUMBER,
                                     [DynamoDocumentMetadataTableFields.LOCATION])
        assert len(actual) == 5
        assert "s3://" in actual[0]
        assert "dev-document-store" in actual[0]


def test_find_docs_returns_empty_response():
    with patch.object(DynamoQueryService, "__call__", return_value=MOCK_EMPTY_RESPONSE):
        actual = find_document_locations(NHS_NUMBER)
        assert actual == []


def test_exception_thrown_by_dynamo():
    error = {"Error": {"Code": 500, "Message": "DynamoDB is down"}}

    exception = ClientError(error, "Query")
    with patch.object(DynamoQueryService, "__call__", side_effect=exception):
        try:
            find_document_locations(NHS_NUMBER)
            assert False
        except ClientError:
            assert True


def test_lambda_handler_returns_400_when_id_not_valid(invalid_nhs_id_event, context):
    with patch.dict(os.environ, PATCH_DYNAMO_TABLES_ENV_VAR):
        expected = ApiGatewayResponse(
            400, "Invalid NHS number", "GET"
        ).create_api_gateway_response()
        actual = lambda_handler(invalid_nhs_id_event, context)
        assert expected == actual


def test_lambda_handler_returns_400_when_id_not_supplied(empty_nhs_id_event, context):
    with patch.dict(os.environ, PATCH_DYNAMO_TABLES_ENV_VAR):
        expected = ApiGatewayResponse(
            400, "Please supply an NHS number", "GET"
        ).create_api_gateway_response()
        actual = lambda_handler(empty_nhs_id_event, context)
        assert expected == actual
