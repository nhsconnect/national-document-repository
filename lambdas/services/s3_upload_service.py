import os
import logging
import uuid
import boto3

from botocore.exceptions import ClientError
from models.nhs_document_reference import NHSDocumentReference

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class S3UploadService:
    s3_object_key = str(uuid.uuid4())

    def __init__(self, s3_bucket_name):
        self.s3_bucket_name = s3_bucket_name

    # Generate a presigned S3 POST URL
    # The response contains the presigned URL and required fields
    def create_document_presigned_url_handler(self, s3_object_key):
        s3_client = boto3.client("s3", region_name="eu-west-2")

        try:
            response = s3_client.generate_presigned_post(
                self.s3_bucket_name, s3_object_key, Fields=None, Conditions=None, ExpiresIn=1800
            )
        except ClientError as e:
            logger.error(e)
            return None

        return response

    # Previously Create Document Reference Object
    # Creates the necessary data to upload to Dynamo DocumentReferenceMetadata table
    def create_document_dynamo_reference_object(
            self, s3_object_key: str, document_request_body
    ):
        s3_file_location = f"s3://{self.s3_bucket_name}/{s3_object_key}"
        logger.info(f"Input document reference location: {s3_file_location}")

        new_document = NHSDocumentReference(
            file_location=s3_file_location,
            reference_id=s3_object_key,
            data=document_request_body,
        )

        logger.info(f"Input document reference filename: {new_document.file_name}")
        return new_document
