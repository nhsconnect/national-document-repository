import os
from unittest import TestCase
from unittest.mock import MagicMock, patch

import boto3
import moto

from lambdas.create_document_reference import (
    create_document_presigned_url_handler,
    create_document_reference_object,
    save_document_reference_in_dynamo_db,
)
from lambdas.nhs_document_reference import NHSDocumentReference


@moto.mock_dynamodb
@moto.mock_s3
class TestCreateDocumentReference(TestCase):
    def setUp(self) -> None:
        self.test_s3_bucket_name = "unit_test_s3_bucket"
        os.environ["DOCUMENT_STORE_BUCKET_NAME"] = self.test_s3_bucket_name
        self.test_dynamoDB_table = "unit_test_dynamoDB_table"
        os.environ["DOCUMENT_STORE_DYNAMODB_NAME"] = self.test_dynamoDB_table
        self.test_s3_object_key = "1234-4567-8912-HSDF-TEST"
        s3_client = boto3.client("s3", region_name="eu-west-2")
        self.test_bucket = s3_client.create_bucket(
            Bucket=self.test_s3_bucket_name,
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )
        dynamodb = boto3.resource("dynamodb")
        self.test_table = dynamodb.create_table(
            TableName=self.test_dynamoDB_table,
            AttributeDefinitions=[
                {"AttributeName": "NhsNumber", "AttributeType": "N"},
                {"AttributeName": "FileName", "AttributeType": "S"},
                {"AttributeName": "FileLocation", "AttributeType": "S"},
                {"AttributeName": "Created", "AttributeType": "S"},
                {"AttributeName": "ContentType", "AttributeType": "S"},
                {"AttributeName": "VirusScannerResult", "AttributeType": "S"},
            ],
            KeySchema=[
                {"AttributeName": "NhsNumber", "KeyType": "HASH"},
                {"AttributeName": "FileName", "KeyType": "HASH"},
                {"AttributeName": "FileLocation", "KeyType": "HASH"},
                {"AttributeName": "Created", "KeyType": "HASH"},
                {"AttributeName": "ContentType", "KeyType": "HASH"},
                {"AttributeName": "VirusScannerResult", "KeyType": "HASH"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        self.mocked_presigned_response = {
            "url": "https://unit_test_s3_bucket.s3.amazonaws.com/",
            "fields": {
                "key": "test",
                "x-amz-algorithm": "TEST-test",
                "x-amz-credential": "TEST-test",
                "x-amz-date": "20230801T105444Z",
                "x-amz-security-token": "test-TEST",
                "policy": "test-TEST=",
                "x-amz-signature": "test-TEST",
            },
        }
        self.mocked_event_body = {
            "resourceType": "DocumentReference",
            "subject": {"identifier": {"value": 111111000}},
            "content": [{"attachment": {"contentType": "document.type"}}],
            "description": "document.name",
        }
        self.test_document_location = (
            "s3://" + self.test_s3_bucket_name + "/" + self.test_s3_object_key
        )

    @patch("botocore.signers.generate_presigned_post")
    def test_create_presigned_url(self, mock_generate_presigned_post: MagicMock):
        mock_generate_presigned_post.return_value = self.mocked_presigned_response
        test_return_value = create_document_presigned_url_handler(
            self.test_s3_bucket_name, self.test_s3_object_key
        )
        self.assertEqual(test_return_value, self.mocked_presigned_response)
        mock_generate_presigned_post.assert_called_once()

    def test_create_document_reference_object(self):
        test_document_object = create_document_reference_object(
            self.test_s3_bucket_name, self.test_s3_object_key, self.mocked_event_body
        )
        self.assertEqual(test_document_object.file_name, "document.name")
        self.assertEqual(test_document_object.content_type, "document.type")
        self.assertEqual(test_document_object.nhs_number, 111111000)
        self.assertEqual(
            test_document_object.file_location, self.test_document_location
        )

    @patch("boto3.dynamodb.table.put_item")
    def test_create_document_reference_in_dynamo_db(self, mock_put_item: MagicMock):
        test_document_object = NHSDocumentReference(
            self.test_document_location, self.test_s3_object_key, self.mocked_event_body
        )
        save_document_reference_in_dynamo_db(test_document_object)
        mock_put_item.assert_called_once()

    def tearDown(self) -> None:
        s3_resource = boto3.resource("s3", region_name="eu-west-2")
        s3_bucket = s3_resource.Bucket(self.test_s3_bucket_name)
        for key in s3_bucket.objects.all():
            key.delete()
        s3_bucket.delete()
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table(self.test_dynamoDB_table)
        table.delete()
