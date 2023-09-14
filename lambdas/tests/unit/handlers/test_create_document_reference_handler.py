import json
import os
from unittest.mock import patch, ANY

import pytest
from botocore.exceptions import ClientError
from handlers.create_document_reference_handler import lambda_handler
from services.dynamo_reference_service import DynamoReferenceService
from services.s3_upload_service import S3UploadService
from utils.lambda_response import ApiGatewayResponse

REGION_NAME = "eu-west-2"
MOCK_BUCKET_ARF = "test_arf_s3_bucket"
MOCK_DYNAMODB_ARF = "test_arf_dynamoDB_table"
MOCK_BUCKET_LG = "test_lg_s3_bucket"
MOCK_DYNAMODB_LG = "test_lg_dynamoDB_table"
TEST_OBJECT_KEY = "1234-4567-8912-HSDF-TEST"
TEST_DOCUMENT_LOCATION_ARF = f"s3://{MOCK_BUCKET_ARF}/{TEST_OBJECT_KEY}"
TEST_DOCUMENT_LOCATION_LG = f"s3://{MOCK_BUCKET_LG}/{TEST_OBJECT_KEY}"
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


def test_creates_document_reference_and_returns_presigned_url_with_arf_document_type(arf_document_type_event, context, mocker):
    os.environ["DOCUMENT_STORE_DYNAMODB_NAME"] = MOCK_DYNAMODB_ARF
    os.environ["DOCUMENT_STORE_BUCKET_NAME"] = MOCK_BUCKET_ARF
    os.environ["LLOYD_GEORGE_DYNAMODB_NAME"] = MOCK_DYNAMODB_LG
    os.environ["LLOYD_GEORGE_BUCKET_NAME"] = MOCK_BUCKET_LG

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

                actual = lambda_handler(arf_document_type_event, context)

                assert actual == expected

def test_request_with_arf_document_type_uses_arf_environment_variables(arf_document_type_event, context, mocker):
    os.environ["DOCUMENT_STORE_DYNAMODB_NAME"] = MOCK_DYNAMODB_ARF
    os.environ["DOCUMENT_STORE_BUCKET_NAME"] = MOCK_BUCKET_ARF
    os.environ["LLOYD_GEORGE_DYNAMODB_NAME"] = MOCK_DYNAMODB_LG
    os.environ["LLOYD_GEORGE_BUCKET_NAME"] = MOCK_BUCKET_LG

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
        ) as create_document_presigned_url_handler_mock :
            with patch.object(
                DynamoReferenceService, "save_document_reference_in_dynamo_db"
            ) as save_document_reference_in_dynamo_db_mock:

                response = lambda_handler(arf_document_type_event, context)
            
            save_document_reference_in_dynamo_db_mock.assert_called_once_with(MOCK_DYNAMODB_ARF, mock_doc_ref)

        create_document_presigned_url_handler_mock.assert_called_once_with(MOCK_BUCKET_ARF, ANY)

def test_request_with_lg_document_type_uses_lg_environment_variables(lg_document_type_event, context, mocker):
    os.environ["DOCUMENT_STORE_DYNAMODB_NAME"] = MOCK_DYNAMODB_ARF
    os.environ["DOCUMENT_STORE_BUCKET_NAME"] = MOCK_BUCKET_ARF
    os.environ["LLOYD_GEORGE_DYNAMODB_NAME"] = MOCK_DYNAMODB_LG
    os.environ["LLOYD_GEORGE_BUCKET_NAME"] = MOCK_BUCKET_LG

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
        ) as create_document_presigned_url_handler_mock :
            with patch.object(
                DynamoReferenceService, "save_document_reference_in_dynamo_db"
            ) as save_document_reference_in_dynamo_db_mock:

                response = lambda_handler(lg_document_type_event, context)
            
            save_document_reference_in_dynamo_db_mock.assert_called_once_with(MOCK_DYNAMODB_LG, mock_doc_ref)

        create_document_presigned_url_handler_mock.assert_called_once_with(MOCK_BUCKET_LG, ANY)

       

def test_creates_document_reference_and_returns_presigned_url_with_lg_document_type(lg_document_type_event, context, mocker):
    os.environ["DOCUMENT_STORE_DYNAMODB_NAME"] = MOCK_DYNAMODB_ARF
    os.environ["DOCUMENT_STORE_BUCKET_NAME"] = MOCK_BUCKET_ARF
    os.environ["LLOYD_GEORGE_DYNAMODB_NAME"] = MOCK_DYNAMODB_LG
    os.environ["LLOYD_GEORGE_BUCKET_NAME"] = MOCK_BUCKET_LG

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

                actual = lambda_handler(lg_document_type_event, context)

                assert actual == expected
                assert DynamoReferenceService


def test_returns_400_response_when_invalid_document_type_is_provided(invalid_document_type_event, context, mocker):
    os.environ["DOCUMENT_STORE_DYNAMODB_NAME"] = MOCK_DYNAMODB_ARF
    os.environ["DOCUMENT_STORE_BUCKET_NAME"] = MOCK_BUCKET_ARF
    os.environ["LLOYD_GEORGE_DYNAMODB_NAME"] = MOCK_DYNAMODB_LG
    os.environ["LLOYD_GEORGE_BUCKET_NAME"] = MOCK_BUCKET_LG

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
                    400, "An error occured processing the required document type", "POST"
                ).create_api_gateway_response()

                actual = lambda_handler(invalid_document_type_event, context)

                assert actual == expected


def test_returns_400_when_error_connecting_to_aws_resources(arf_document_type_event, context, mocker):
    os.environ["DOCUMENT_STORE_DYNAMODB_NAME"] = MOCK_DYNAMODB_ARF
    os.environ["DOCUMENT_STORE_BUCKET_NAME"] = MOCK_BUCKET_ARF
    os.environ["LLOYD_GEORGE_DYNAMODB_NAME"] = MOCK_DYNAMODB_LG
    os.environ["LLOYD_GEORGE_BUCKET_NAME"] = MOCK_BUCKET_LG

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

                actual = lambda_handler(arf_document_type_event, context)

                assert actual == expected
