import os

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

