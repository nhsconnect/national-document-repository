import os

DEFAULT_REGION = "eu-west-2"


def get_aws_region() -> str:
    return os.environ.get("AWS_REGION", DEFAULT_REGION)
