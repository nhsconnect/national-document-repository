import os

import pytest

from handlers.virus_scan_handler import lambda_handler
from models.virus_scan import ScanResult


@pytest.fixture
def patch_env_vars(mocker):
    patched_env_vars = {
        "DOCUMENT_STORE_DYNAMODB_NAME": "mock_arf_dynamo",
        "DOCUMENT_STORE_BUCKET_NAME": "mock_arf_s3",
        "LLOYD_GEORGE_DYNAMODB_NAME": "mock_lg_dynamo",
        "LLOYD_GEORGE_BUCKET_NAME": "mock_lg_s3",
    }
    mocker.patch.dict(os.environ, patched_env_vars)
    yield patched_env_vars


@pytest.fixture
def mock_dynamodb_service(mocker, patch_env_vars):
    mocked = mocker.MagicMock()
    mocker.patch("handlers.virus_scan_handler.DynamoDBService", return_value=mocked)
    yield mocked


def test_lambda_handler_update_dynamo_for_clean_result(
    patch_env_vars, mock_dynamodb_service
):
    test_file_name = "9000000009/test_file.pdf"

    test_event = build_test_event(
        bucket_name=patch_env_vars["DOCUMENT_STORE_BUCKET_NAME"],
        key=test_file_name,
        result=ScanResult.CLEAN,
    )

    lambda_handler(test_event, None)

    expected_file_location = (
        f"s3://{patch_env_vars['DOCUMENT_STORE_BUCKET_NAME']}/{test_file_name}"
    )
    expected_scan_result = ScanResult.CLEAN

    mock_dynamodb_service.update_item_service.assert_called_with(
        table_name=patch_env_vars["DOCUMENT_STORE_DYNAMODB_NAME"],
        key={"ID": test_file_name},
        update_expression="SET VirusScannerResult=:result, FileLocation=:location, documentUploaded=:true",
        expression_attribute_values={
            ":result": {"S": expected_scan_result},
            ":location": {"S": expected_file_location},
            ":true": {"BOOL": True},
        },
    )


def build_test_event(bucket_name: str, key: str, result: str) -> dict:
    return {
        "Records": [
            {
                "EventVersion": "1.0",
                "EventSubscriptionArn": "arn:aws:sns:eu-west-2:123456789012:sns-lambda:mock-arn-id",
                "EventSource": "aws:sns",
                "Sns": {
                    "SignatureVersion": "1",
                    "Timestamp": "2023-09-25T12:34:56.789Z",
                    "Signature": "mock-sign",
                    "SigningCertUrl": "https://mock-url/mock.pem",
                    "MessageId": "mock-message-id",
                    "Message": {
                        "bucketName": bucket_name,
                        "key": key,
                        "result": result,
                    },
                    "Type": "Notification",
                    "UnsubscribeUrl": "https://mock-url/unsubscribe",
                    "TopicArn": "arn:aws:sns:us-east-1:123456789012:sns-lambda",
                    "Subject": "TestInvoke",
                },
            }
        ]
    }
