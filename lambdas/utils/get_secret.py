import logging

import boto3
from botocore.exceptions import ClientError

from utils.get_aws_region import get_aws_region

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_secret(secret_name: str) -> str:
    # read a secret value from AWS Secrets Manager
    client = boto3.client("secretsmanager", region_name=get_aws_region())

    try:
        response = client.get_secret_value(SecretId=secret_name)
        return response["SecretString"]
    except ClientError as e:
        logger.info(f"Got error when retrieving secret {secret_name}")
        logger.error(e)
        raise e
