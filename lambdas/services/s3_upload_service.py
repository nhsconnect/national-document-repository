import logging
import uuid

import boto3
from botocore.exceptions import ClientError

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
                self.s3_bucket_name,
                s3_object_key,
                Fields=None,
                Conditions=None,
                ExpiresIn=1800,
            )
        except ClientError as e:
            logger.error(e)
            return None

        return response
