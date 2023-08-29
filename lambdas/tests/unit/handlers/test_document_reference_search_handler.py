from dataclasses import dataclass
from unittest import mock
from unittest.mock import MagicMock, patch

import boto3
import pytest

from moto import mock_dynamodb

from handlers.document_reference_search_handler import lambda_handler
from utils.lambda_response import ApiGatewayResponse

MOCK_RESPONSE = {"Items": [
    {
        "FileName": "Screenshot 2023-08-16 at 15.26.11.png",
        "Created": "2023-08-23T00:38:04.103Z"
    },
    {
        "FileName": "GIF.gif",
        "Created": "2023-08-22T17:38:31.890Z"
    },
    {
        "FileName": "Screen Recording 2023-08-15 at 16.18.31.mov",
        "Created": "2023-08-23T00:38:04.095Z"
    },
    {
        "FileName": "screenshot guidance.png",
        "Created": "2023-08-22T23:39:27.178Z"
    },
    {
        "FileName": "Screenshot 2023-08-15 at 16.17.56.png",
        "Created": "2023-08-23T00:38:04.101Z"
    }
],
    "Count": 5,
    "ScannedCount": 5,
    "ResponseMetadata": {
        "RequestId": "JHJBP4GU007VMB2V8C9NEKUL8VVV4KQNSO5AEMVJF66Q9ASUAAJG",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {
            "server": "Server",
            "date": "Tue, 29 Aug 2023 11:08:21 GMT",
            "content-type": "application/x-amz-json-1.0",
            "content-length": "510",
            "connection": "keep-alive",
            "x-amzn-requestid": "JHJBP4GU007VMB2V8C9NEKUL8VVV4KQNSO5AEMVJF66Q9ASUAAJG",
            "x-amz-crc32": "820258331"
        },
        "RetryAttempts": 0
    }
}

MOCK_EMPTY_RESPONSE = {"Items": [
],
    "Count": 5,
    "ScannedCount": 5,
    "ResponseMetadata": {
        "RequestId": "JHJBP4GU007VMB2V8C9NEKUL8VVV4KQNSO5AEMVJF66Q9ASUAAJG",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {
            "server": "Server",
            "date": "Tue, 29 Aug 2023 11:08:21 GMT",
            "content-type": "application/x-amz-json-1.0",
            "content-length": "510",
            "connection": "keep-alive",
            "x-amzn-requestid": "JHJBP4GU007VMB2V8C9NEKUL8VVV4KQNSO5AEMVJF66Q9ASUAAJG",
            "x-amz-crc32": "820258331"
        },
        "RetryAttempts": 0
    }
}

EXPECTED_RESPONSE = [
    {
        "FileName": "Screenshot 2023-08-16 at 15.26.11.png",
        "Created": "2023-08-23T00:38:04.103Z"
    },
    {
        "FileName": "GIF.gif",
        "Created": "2023-08-22T17:38:31.890Z"
    },
    {
        "FileName": "Screen Recording 2023-08-15 at 16.18.31.mov",
        "Created": "2023-08-23T00:38:04.095Z"
    },
    {
        "FileName": "screenshot guidance.png",
        "Created": "2023-08-22T23:39:27.178Z"
    },
    {
        "FileName": "Screenshot 2023-08-15 at 16.17.56.png",
        "Created": "2023-08-23T00:38:04.101Z"
    }
]


@pytest.fixture
def valid_nhs_id_event():
    api_gateway_proxy_event = {
        "queryStringParameters": {"patientId": "9000000009"},
    }
    return api_gateway_proxy_event


@pytest.fixture
def context():
    @dataclass
    class LambdaContext:
        function_name: str = "test"
        aws_request_id: str = "88888888-4444-4444-4444-121212121212"
        invoked_function_arn: str = (
            "arn:aws:lambda:eu-west-1:123456789101:function:test"
        )

    return LambdaContext()


@pytest.fixture
def mock_boto3_dynamo():
    return MagicMock()


@pytest.fixture
def mock_dynamo_table():
    return MagicMock()


def test_lambda_handler_returns_items_from_dynamo(valid_nhs_id_event, context, mock_dynamo_table, mock_boto3_dynamo):
    with patch.object(boto3, "resource", return_value=mock_boto3_dynamo):
        mock_boto3_dynamo.Table.return_value = mock_dynamo_table
        mock_dynamo_table.query.return_value = MOCK_RESPONSE
        expected = ApiGatewayResponse(200, EXPECTED_RESPONSE, "GET")
        actual = lambda_handler(valid_nhs_id_event, context)
        assert expected == actual


def test_lambda_handler_returns_200_empty_list_when_dynamo_returns_no_records(valid_nhs_id_event, context,
                                                                              mock_dynamo_table,
                                                                              mock_boto3_dynamo):
    with patch.object(boto3, "resource", return_value=mock_boto3_dynamo):
        mock_boto3_dynamo.Table.return_value = mock_dynamo_table
        mock_dynamo_table.query.return_value = MOCK_EMPTY_RESPONSE
        expected = ApiGatewayResponse(200, [], "GET")
        actual = lambda_handler(valid_nhs_id_event, context)
        assert expected == actual


def test_lambda_handler_returns_500_when_dynamo_has_unexpected_response(valid_nhs_id_event, context,
                                                                        mock_dynamo_table,
                                                                        mock_boto3_dynamo):
    with patch.object(boto3, "resource", return_value=mock_boto3_dynamo):
        mock_boto3_dynamo.Table.return_value = mock_dynamo_table
        mock_dynamo_table.query.return_value = {}
        expected = ApiGatewayResponse(500, "Unrecognised response from DynamoDB", "GET")
        actual = lambda_handler(valid_nhs_id_event, context)
        assert expected == actual
