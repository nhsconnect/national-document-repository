import hashlib

import boto3
from botocore.exceptions import ClientError
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)

# AWS Clients
ssm_client = boto3.client("ssm", region_name="us-east-1")
dynamodb_client = boto3.client("dynamodb", region_name="eu-west-2")
table_name = "ndrd_CloudFrontEdgeReference"

# Responses
internal_server_error_response = {
    "status": "500",
    "statusDescription": "Internal Server Error xD",
    "headers": {
        "content-type": [{"key": "Content-Type", "value": "text/plain"}],
        "content-encoding": [{"key": "Content-Encoding", "value": "UTF-8"}],
    },
    "body": "Internal Server Error xD",
}

forbidden_response = {
    "status": "403",
    "statusDescription": "Forbidden",
    "headers": {
        "content-type": [{"key": "Content-Type", "value": "text/plain"}],
        "content-encoding": [{"key": "Content-Encoding", "value": "UTF-8"}],
    },
    "body": "Forbidden",
}


def lambda_handler(event, context):
    request = event["Records"][0]["cf"]["request"]
    uri = request["uri"]
    querystring = request.get("querystring", "")

    uri_hash = hashlib.md5(f"{uri}?{querystring}".encode("utf-8")).hexdigest()

    try:
        if is_already_used(uri_hash):
            return forbidden_response
        save_usage(uri_hash)
    except ClientError as e:
        logger.error(
            f"ClientError: {str(e)}",
            {"Result": "Lloyd George stitching failed"},
        )
        return internal_server_error_response

    return request


def is_already_used(hash):
    response = dynamodb_client.get_item(TableName=table_name, Key={"pk": {"S": hash}})
    return "Item" in response


def save_usage(hash):
    dynamodb_client.put_item(TableName=table_name, Item={"pk": {"S": hash}})
