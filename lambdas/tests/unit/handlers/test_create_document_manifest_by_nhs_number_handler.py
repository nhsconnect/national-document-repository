from unittest.mock import patch

from handlers.create_document_manifest_by_nhs_number_handler import find_document_locations
from services.dynamo_query_service import DynamoQueryService
from helpers.dynamo_responses import LOCATION_QUERY_RESPONSE, MOCK_EMPTY_RESPONSE
from botocore.exceptions import ClientError

NHS_NUMBER = 1111111111


def test_find_docs_retrieves_something():
    with patch.object(DynamoQueryService, "__call__", return_value=LOCATION_QUERY_RESPONSE):
        actual = find_document_locations(NHS_NUMBER)
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
