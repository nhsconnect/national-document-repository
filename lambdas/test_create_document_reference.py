import os
from unittest import TestCase
from unittest.mock import MagicMock, patch

import boto3
import moto

from lambdas.create_document_reference import create_document_reference_handler


@moto.mock_s3
class TestCreateDocumentReference(TestCase):
    def setUp(self) -> None:
        self.test_s3_bucket_name = "unit_test_s3_bucket"
        os.environ["DOCUMENT_STORE_BUCKET_NAME"] = self.test_s3_bucket_name

        s3_client = boto3.client('s3', region_name="eu-west-2")
        s3_client.create_bucket(Bucket = self.test_s3_bucket_name, CreateBucketConfiguration={'LocationConstraint': 'eu-west-2'})

        self.mocked_presigned_response ={
                "url": "https://unit_test_s3_bucket.s3.amazonaws.com/",
                "fields": {
                    "key": "test",
                    "x-amz-algorithm": "TEST-test",
                    "x-amz-credential": "TEST-test",
                    "x-amz-date": "20230801T105444Z",
                    "x-amz-security-token": "test-TEST",
                    "policy": "test-TEST=",
                    "x-amz-signature": "test-TEST"
                }
        }
    @patch('botocore.signers.generate_presigned_post')
    def test_create_presigned_url(self, mock_generate_presigned_post : MagicMock) -> None:
        mock_generate_presigned_post.return_value = self.mocked_presigned_response
        test_return_value = create_document_reference_handler(event=None, context=None)
        self.assertEqual(test_return_value, self.mocked_presigned_response)
        mock_generate_presigned_post.assert_called_once()

    def tearDown(self) -> None:
        s3_resource = boto3.resource('s3', region_name="eu-west-2")
        s3_bucket = s3_resource.Bucket( self.test_s3_bucket_name )
        for key in s3_bucket.objects.all():
            key.delete()
        s3_bucket.delete()
