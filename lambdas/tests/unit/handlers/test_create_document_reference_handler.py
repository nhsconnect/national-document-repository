import os

from handlers.create_document_reference_handler import (
    create_document_presigned_url_handler, create_document_reference_object,
    save_document_reference_in_dynamo_db)
from models.nhs_document_reference import NHSDocumentReference

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

os.environ["DOCUMENT_STORE_DYNAMODB_NAME"] = MOCK_DYNAMODB


def test_create_presigned_url(mocker):
    mock_generate_presigned_post = mocker.patch(
        "botocore.signers.generate_presigned_post"
    )

    mocked_presigned_response = {
        "url": "https://test_s3_bucket.s3.amazonaws.com/",
        "fields": {
            "key": "test",
            "x-amz-algorithm": "test",
            "x-amz-credential": "test",
            "x-amz-date": "20230801T105444Z",
            "x-amz-security-token": "test",
            "policy": "test",
            "x-amz-signature": "test",
        },
    }

    mock_generate_presigned_post.return_value = mocked_presigned_response

    test_return_value = create_document_presigned_url_handler(
        MOCK_BUCKET, TEST_OBJECT_KEY
    )

    assert test_return_value == mocked_presigned_response
    mock_generate_presigned_post.assert_called_once()


def test_create_document_reference_object():
    test_document_object = create_document_reference_object(
        MOCK_BUCKET, TEST_OBJECT_KEY, MOCK_EVENT_BODY
    )
    assert test_document_object.file_name == "test_filename.pdf"
    assert test_document_object.content_type == "application/pdf"
    assert test_document_object.nhs_number == 111111000
    assert test_document_object.file_location == TEST_DOCUMENT_LOCATION


def test_create_document_reference_in_dynamo_db(mocker):
    mock_dynamo = mocker.patch("boto3.resource")
    mock_table = mocker.MagicMock()

    test_document_object = NHSDocumentReference(
        TEST_OBJECT_KEY, TEST_DOCUMENT_LOCATION, MOCK_EVENT_BODY
    )

    mock_dynamo.return_value.Table.return_value = mock_table

    save_document_reference_in_dynamo_db(test_document_object)
    mock_table.put_item.assert_called_once()
