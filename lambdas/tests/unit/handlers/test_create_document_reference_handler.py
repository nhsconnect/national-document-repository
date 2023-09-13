import json
import os
from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError
from handlers.create_document_reference_handler import lambda_handler
from services.dynamo_reference_service import DynamoReferenceService
from services.s3_upload_service import S3UploadService
from utils.lambda_response import ApiGatewayResponse

REGION_NAME = "eu-west-2"
MOCK_BUCKET = "test_s3_bucket"
MOCK_DYNAMODB = "test_dynamoDB_table"
TEST_OBJECT_KEY = "1234-4567-8912-HSDF-TEST"
TEST_DOCUMENT_LOCATION = f"s3://{MOCK_BUCKET}/{TEST_OBJECT_KEY}"
MOCK_EVENT_BODY = {
    "resourceType": "DocumentReference",
    "subject": {"identifier": {"value": 111111000}},
    "content": [{"attachment": {"contentType": "application/pdf"}}],
    "description": "test_filename.pdf",
}

MOCK_PRESIGNED_POST_RESPONSE = {
    "url": "https://ndr-dev-document-store.s3.amazonaws.com/",
    "fields": {
        "key": "0abed67c-0d0b-4a11-a600-a2f19ee61281",
        "x-amz-algorithm": "AWS4-HMAC-SHA256",
        "x-amz-credential": "ASIAXYSUA44VTL5M5LWL/20230911/eu-west-2/s3/aws4_request",
        "x-amz-date": "20230911T084756Z",
        "x-amz-security-token": "test-security-token",
        "policy": "test-policy",
        "x-amz-signature": "b6afcf8b27fc883b0e0a25a789dd2ab272ea4c605a8c68267f73641d7471132f",
    },
}


@pytest.fixture
def event():
    api_gateway_proxy_event = {"body": '{"test":"blah"}'}
    return api_gateway_proxy_event


def test_creates_document_reference_and_returns_presigned_url(event, context, mocker):
    os.environ["DOCUMENT_STORE_DYNAMODB_NAME"] = MOCK_DYNAMODB
    os.environ["DOCUMENT_STORE_BUCKET_NAME"] = MOCK_BUCKET

    mock_doc_ref = mocker.MagicMock()

    with patch.object(
        DynamoReferenceService,
        "create_document_dynamo_reference_object",
        return_value=mock_doc_ref,
    ):
        with patch.object(
            S3UploadService,
            "create_document_presigned_url_handler",
            return_value=MOCK_PRESIGNED_POST_RESPONSE,
        ):
            with patch.object(
                DynamoReferenceService, "save_document_reference_in_dynamo_db"
            ):
                expected = ApiGatewayResponse(
                    200, json.dumps(MOCK_PRESIGNED_POST_RESPONSE), "POST"
                ).create_api_gateway_response()

                actual = lambda_handler(event, context)

                assert actual == expected


def test_returns_500_when_error_connecting_to_aws_resources(event, context, mocker):
    os.environ["DOCUMENT_STORE_DYNAMODB_NAME"] = MOCK_DYNAMODB
    os.environ["DOCUMENT_STORE_BUCKET_NAME"] = MOCK_BUCKET

    error = {"Error": {"Code": 500, "Message": "DynamoDB is down"}}
    exception = ClientError(error, "Query")

    mock_doc_ref = mocker.MagicMock()

    with patch.object(
        DynamoReferenceService,
        "create_document_dynamo_reference_object",
        return_value=mock_doc_ref,
    ):
        with patch.object(
            S3UploadService,
            "create_document_presigned_url_handler",
            side_effect=exception,
        ):
            with patch.object(
                DynamoReferenceService, "save_document_reference_in_dynamo_db"
            ):
                expected = ApiGatewayResponse(
                    400, "An error occurred when getting ready to upload", "POST"
                ).create_api_gateway_response()

                actual = lambda_handler(event, context)

                assert actual == expected
