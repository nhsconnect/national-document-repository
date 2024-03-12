from typing import Any, Mapping

import boto3
from botocore.client import Config as BotoConfig
from botocore.exceptions import ClientError
from utils.audit_logging_setup import LoggingService
from utils.exceptions import TagNotFoundException

logger = LoggingService(__name__)


class S3Service:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialised = False
        return cls._instance

    def __init__(self):
        if not self.initialised:
            config = BotoConfig(
                retries={"max_attempts": 3, "mode": "standard"},
                s3={"addressing_style": "virtual"},
                signature_version="s3v4",
            )
            self.client = boto3.client("s3", config=config)
            self.presigned_url_expiry = 1800
            self.initialised = True

    # S3 Location should be a minimum of a s3_object_key but can also be a directory location in the form of
    # {{directory}}/{{s3_object_key}}
    def create_upload_presigned_url(self, s3_bucket_name: str, s3_object_location: str):
        return self.client.generate_presigned_post(
            s3_bucket_name,
            s3_object_location,
            Fields=None,
            Conditions=None,
            ExpiresIn=self.presigned_url_expiry,
        )

    def create_download_presigned_url(self, s3_bucket_name: str, file_key: str):
        logger.info("Generating presigned URL for manifest")
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": s3_bucket_name, "Key": file_key},
            ExpiresIn=self.presigned_url_expiry,
        )

    def download_file(self, s3_bucket_name: str, file_key: str, download_path: str):
        return self.client.download_file(s3_bucket_name, file_key, download_path)

    def upload_file(self, file_name: str, s3_bucket_name: str, file_key: str):
        return self.client.upload_file(file_name, s3_bucket_name, file_key)

    def upload_file_with_extra_args(
        self,
        file_name: str,
        s3_bucket_name: str,
        file_key: str,
        extra_args: Mapping[str, Any],
    ):
        return self.client.upload_file(file_name, s3_bucket_name, file_key, extra_args)

    def copy_across_bucket(
        self,
        source_bucket: str,
        source_file_key: str,
        dest_bucket: str,
        dest_file_key: str,
    ):
        return self.client.copy_object(
            Bucket=dest_bucket,
            Key=dest_file_key,
            CopySource={"Bucket": source_bucket, "Key": source_file_key},
        )

    def delete_object(self, s3_bucket_name: str, file_key: str):
        return self.client.delete_object(Bucket=s3_bucket_name, Key=file_key)

    def create_object_tag(
        self, s3_bucket_name: str, file_key: str, tag_key: str, tag_value: str
    ):
        return self.client.put_object_tagging(
            Bucket=s3_bucket_name,
            Key=file_key,
            Tagging={
                "TagSet": [
                    {"Key": tag_key, "Value": tag_value},
                ]
            },
        )

    def get_tag_value(self, s3_bucket_name: str, file_key: str, tag_key: str) -> str:
        response = self.client.get_object_tagging(
            Bucket=s3_bucket_name,
            Key=file_key,
        )
        for key_value_pair in response["TagSet"]:
            if key_value_pair["Key"] == tag_key:
                return key_value_pair["Value"]

        raise TagNotFoundException(
            f"Object {file_key} doesn't have a tag of key {tag_key}"
        )

    def file_exist_on_s3(self, s3_bucket_name: str, file_key: str) -> bool:
        try:
            response = self.client.head_object(Bucket=s3_bucket_name, Key=file_key)
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                return True
            return False
        except (KeyError, AttributeError) as e:
            logger.info(str(e), {"Result": "Failed to check if file exists on s3"})
            return False
        except ClientError as e:
            error_message = str(e)
            if (
                "An error occurred (403)" in error_message
                or "An error occurred (404)" in error_message
            ):
                return False
            logger.error(str(e), {"Result": "Failed to check if file exists on s3"})
            raise e
