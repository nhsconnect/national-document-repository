import json
import os
from unittest.mock import ANY

import pytest
from botocore.exceptions import ClientError
from handlers.create_document_reference_handler import lambda_handler
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

def setEnvironmentVariables():
    os.environ["DOCUMENT_STORE_DYNAMODB_NAME"] = MOCK_DYNAMODB_ARF
    os.environ["DOCUMENT_STORE_BUCKET_NAME"] = MOCK_BUCKET_ARF
    os.environ["LLOYD_GEORGE_DYNAMODB_NAME"] = MOCK_DYNAMODB_LG
    os.environ["LLOYD_GEORGE_BUCKET_NAME"] = MOCK_BUCKET_LG

    
@pytest.fixture
def arf_type_event():
    api_gateway_proxy_event = {
        "queryStringParameters": {"documentType": "arf"},
        "body": '{"subject": {"identifier": {"value": "test"}}, '
        '"content": [{"attachment": {"contentType": "test"}}], '
        '"description": "test"}'
    }
    return api_gateway_proxy_event

@pytest.fixture
def lg_type_event():
    api_gateway_proxy_event = {
        "queryStringParameters": {"documentType": "LG"},
        "body": '{"subject": {"identifier": {"value": "test"}}, '
        '"content": [{"attachment": {"contentType": "test"}}], '
        '"description": "test"}'
    }
    return api_gateway_proxy_event


def test_create_document_reference_valid_arf_type_returns_200(set_env, arf_type_event, context, mocker):

    mocker.patch("services.dynamo_service.DynamoDBService.post_item_service")

    mock_presigned = mocker.patch(
        "services.s3_service.S3Service.create_document_presigned_url_handler"
    )
    mock_presigned.return_value = MOCK_PRESIGNED_POST_RESPONSE

    expected = ApiGatewayResponse(
        200, json.dumps(MOCK_PRESIGNED_POST_RESPONSE), "POST"
    ).create_api_gateway_response()

    actual = lambda_handler(arf_type_event, context)

    assert actual == expected

def test_create_document_reference_valid_arf_type_uses_arf_s3_bucket(set_env, arf_type_event, context, mocker):

    # Override the set_env instance
    os.environ["DOCUMENT_STORE_BUCKET_NAME"] = MOCK_BUCKET_ARF
    mocker.patch("services.dynamo_service.DynamoDBService.post_item_service")

    mock_presigned = mocker.patch(
        "services.s3_service.S3Service.create_document_presigned_url_handler"
    )
    mock_presigned.return_value = MOCK_PRESIGNED_POST_RESPONSE

    actual = lambda_handler(arf_type_event, context)

    mock_presigned.assert_called_once_with(MOCK_BUCKET_ARF, ANY)

def test_create_document_reference_valid_arf_type_uses_arf_dynamo_table(set_env, arf_type_event, context, mocker):

    # Override the set_env instance
    os.environ["DOCUMENT_STORE_DYNAMODB_NAME"] = MOCK_DYNAMODB_ARF
    mock_dynamo_request = mocker.patch("services.dynamo_service.DynamoDBService.post_item_service")

    mock_presigned = mocker.patch(
        "services.s3_service.S3Service.create_document_presigned_url_handler"
    )
    mock_presigned.return_value = MOCK_PRESIGNED_POST_RESPONSE

    lambda_handler(arf_type_event, context)
    mock_dynamo_request.assert_called_once_with(MOCK_DYNAMODB_ARF, ANY)

def test_create_document_reference_valid_lg_type_returns_200(set_env, lg_type_event, context, mocker):

    mocker.patch("services.dynamo_service.DynamoDBService.post_item_service")

    mock_presigned = mocker.patch(
        "services.s3_service.S3Service.create_document_presigned_url_handler"
    )
    mock_presigned.return_value = MOCK_PRESIGNED_POST_RESPONSE

    expected = ApiGatewayResponse(
        200, json.dumps(MOCK_PRESIGNED_POST_RESPONSE), "POST"
    ).create_api_gateway_response()

    actual = lambda_handler(lg_type_event, context)

    assert actual == expected

def test_create_document_reference_valid_lg_type_uses_lg_s3_bucket(set_env, lg_type_event, context, mocker):

    # Override the set_env instance
    os.environ["LLOYD_GEORGE_BUCKET_NAME"] = MOCK_BUCKET_LG
    mocker.patch("services.dynamo_service.DynamoDBService.post_item_service")

    mock_presigned = mocker.patch(
        "services.s3_service.S3Service.create_document_presigned_url_handler"
    )
    mock_presigned.return_value = MOCK_PRESIGNED_POST_RESPONSE

    actual = lambda_handler(lg_type_event, context)

    mock_presigned.assert_called_once_with(MOCK_BUCKET_LG, ANY)

def test_create_document_reference_valid_lg_type_uses_lg_dynamo_table(set_env, lg_type_event, context, mocker):

    # Override the set_env instance
    os.environ["LLOYD_GEORGE_DYNAMODB_NAME"] = MOCK_DYNAMODB_LG
    mock_dynamo_request = mocker.patch("services.dynamo_service.DynamoDBService.post_item_service")

    mock_presigned = mocker.patch(
        "services.s3_service.S3Service.create_document_presigned_url_handler"
    )
    mock_presigned.return_value = MOCK_PRESIGNED_POST_RESPONSE

    lambda_handler(lg_type_event, context)
    mock_dynamo_request.assert_called_once_with(MOCK_DYNAMODB_LG, ANY)

def test_create_document_reference_arf_type_dynamo_ClientError_returns_500(
    set_env, arf_type_event, context, mocker
):
    error = {"Error": {"Code": 500, "Message": "S3 is down"}}
    exception = ClientError(error, "Query")

    mock_dynamo = mocker.patch(
        "services.dynamo_service.DynamoDBService.post_item_service"
    )
    mock_dynamo.side_effect = exception

    mock_presigned = mocker.patch(
        "services.s3_service.S3Service.create_document_presigned_url_handler"
    )
    mock_presigned.return_value = MOCK_PRESIGNED_POST_RESPONSE

    expected = ApiGatewayResponse(
        500, "An error occurred when creating document reference", "POST"
    ).create_api_gateway_response()

    actual = lambda_handler(arf_type_event, context)

    assert actual == expected


def test_create_document_reference_arf_type_s3_ClientError_returns_500(
    set_env, arf_type_event, context, mocker
):
    error = {"Error": {"Code": 500, "Message": "DynamoDB is down"}}
    exception = ClientError(error, "Query")

    mocker.patch("services.dynamo_service.DynamoDBService.post_item_service")

    mock_presigned = mocker.patch(
        "services.s3_service.S3Service.create_document_presigned_url_handler"
    )
    mock_presigned.side_effect = exception

    expected = ApiGatewayResponse(
        500, "An error occurred when creating document reference", "POST"
    ).create_api_gateway_response()

    actual = lambda_handler(arf_type_event, context)

    assert actual == expected

environmentVariables = ["DOCUMENT_STORE_BUCKET_NAME", 
                         "DOCUMENT_STORE_DYNAMODB_NAME", 
                         "LLOYD_GEORGE_BUCKET_NAME",
                         "LLOYD_GEORGE_DYNAMODB_NAME"]
@pytest.mark.parametrize('environmentVariable', environmentVariables)
def test_lambda_handler_missing_environment_variables_returns_400(
    monkeypatch, lg_type_event, environmentVariable, context
):
    setEnvironmentVariables()
    monkeypatch.delenv(environmentVariable)
    expected = ApiGatewayResponse(
        400,
        "An error occurred due to missing key: '" + environmentVariable + "'",
        "POST",
    ).create_api_gateway_response()
    actual = lambda_handler(lg_type_event, context)
    assert expected == actual
