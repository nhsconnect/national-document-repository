import hashlib

import boto3
from botocore.exceptions import ClientError
from services.base.dynamo_service import DynamoDBService
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

    dynamo_service = DynamoDBService()
    uri_hash = hashlib.md5(f"{uri}?{querystring}".encode("utf-8")).hexdigest()

    try:
        dynamo_service.update_conditional(
            table_name=table_name,
            key=uri_hash,
            updated_fields={"IsRequested": True},
            condition_expression="attribute_not_exists(IsRequested) OR IsRequested = :false",
            expression_attribute_values={":false": False},
        )
    except ClientError as e:
        logger.error(
            f"ClientError: {str(e)}",
            {"Result": "Lloyd George stitching failed"},
        )
        return internal_server_error_response

    headers = request.get("headers", {})
    if "authorization" in headers:
        del headers["authorization"]
    return request
