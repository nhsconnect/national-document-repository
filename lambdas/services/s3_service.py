from typing import Any, List, Mapping

import boto3
from botocore.client import Config as BotoConfig
from botocore.exceptions import ClientError
from utils.audit_logging_setup import LoggingService
from utils.exceptions import TagNotFoundException

logger = LoggingService(__name__)


class S3Service:
    def __init__(self):
        config = BotoConfig(retries={"max_attempts": 3, "mode": "standard"})
        self.client = boto3.client("s3", config=config)
        self.presigned_url_expiry = 1800

    # S3 Location should be a minimum of a s3_object_key but can also be a directory location in the form of
    # {{directory}}/{{s3_object_key}}
    def create_document_presigned_url_handler(
        self, s3_bucket_name: str, s3_object_location: str
    ):
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
            response = self.client.head_object(Bucket=s3_bucket_name, file_key=file_key)
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                return True
            return False
        except ClientError as e:
            if "An error occurred (403) when calling the HeadObject operation" in str(
                e
            ) or "An error occurred (404) when calling the HeadObject operation" in str(
                e
            ):
                return False
            logger.error("Got unexpected error when try to check file existence on s3:")
            logger.error(e)
            raise e

    def list_objects_by_prefix(self, s3_bucket_name: str, prefix: str) -> List[str]:
        response = self.client.list_objects_v2(Bucket=s3_bucket_name, Prefix=prefix)
        try:
            if response["IsTruncated"] == "true":
                logger.warning(
                    f"Got more than 1000 results while searching for objects with given prefix {prefix}. "
                    "Some results are not returned."
                )

            return [file_object["Key"] for file_object in response["Contents"]]
        except KeyError as e:
            logger.info(f"Got error while searching bucket content: {e}")
            logger.info(
                f"Bucket {s3_bucket_name} doesn't seem to contain any object with prefix {prefix}"
            )
            return []
