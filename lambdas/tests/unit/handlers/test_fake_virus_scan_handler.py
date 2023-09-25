import os
from unittest.mock import patch

from botocore.exceptions import ClientError

from services.dynamo_service import DynamoDBService
from tests.unit.handlers.conftest import context
from handlers.fake_virus_scan_handler import lambda_handler
from helpers.data.s3_responses import MOCK_S3_OBJECT_CREATED
from utils.lambda_response import ApiGatewayResponse


def test_handler_returns_200_response_when_record_updates():
    os.environ["DOCUMENT_STORE_DYNAMODB_NAME"] = "doc_store_dynamo"
    with patch.object(DynamoDBService, "update_item_service", return_value=""):
        expected = ApiGatewayResponse(200, "File marked as Clean", "PATCH").create_api_gateway_response()
        actual = lambda_handler(MOCK_S3_OBJECT_CREATED, context)
        assert actual == expected


def test_handler_returns_500_response_when_service_fails_to_update_dynamo():
    os.environ["DOCUMENT_STORE_DYNAMODB_NAME"] = "doc_store_dynamo"
    expected_error = ClientError(
        {"Error": {"Code": 500, "Message": "test error"}}, "testing"
    )
    with patch.object(DynamoDBService, "update_item_service", side_effect=expected_error):
        expected = ApiGatewayResponse(500, "Unable to mark file as clean", "PATCH").create_api_gateway_response()
        actual = lambda_handler(MOCK_S3_OBJECT_CREATED, context)
        assert actual == expected
