from unittest.mock import patch

from handlers.create_document_manifest_by_nhs_number_handler import find_document_locations
from services.dynamo_query_service import DynamoQueryService
from unit.helpers.dynamo_responses import LOCATION_QUERY_RESPONSE, MOCK_EMPTY_RESPONSE
from botocore.exceptions import ClientError

NHS_NUMBER = 1111111111


def test_find_docs_retrieves_something():
    with patch.object(DynamoQueryService, "__call__", return_value=LOCATION_QUERY_RESPONSE):
        actual = find_document_locations(NHS_NUMBER)
        assert len(actual) == 5
        assert actual[0] == "s3://dev-document-store-20230724132334705600000001/0e1ba46f-ab14-4cf2-8750-8bc407417160"


def test_find_docs_returns_empty_response():
    with patch.object(DynamoQueryService, "__call__", return_value=MOCK_EMPTY_RESPONSE):
        actual = find_document_locations(NHS_NUMBER)
        assert actual == []


def test_exception_thrown_by_dynamo():
    error = {"Error": {"Code": 500, "Message": "DynamoDB is down"}}

    exception = ClientError(error, "Query")
    with patch.object(DynamoQueryService, "__call__", side_effect=exception):
        actual = find_document_locations(NHS_NUMBER)



    # Mock the DynamoQueryService for this unit test
    # Example below
    # with patch.object(DynamoQueryService, "__call__", return_value=MOCK_RESPONSE):
    # Refer to test_document_reference_search_handler for examples of patch.object
    # We'd like the output to be list of strings, example: <-- might change later, but ok for now
    # [
    #   's3://rachel-is-cool/abcde-3i421394792837-sdkbcskjdnf',
    #   's3://alex-is-cool/abcde-3i421394792837-sdkbcskjdnf',
    # ]

    # Test it has the s3:// at the start and contains the bucket ID as expected
    # Test for empty response (i.e. response with empty Items)
    # Write a test to see if it responds correctly whern an exception is thrown from the Dynamo service

