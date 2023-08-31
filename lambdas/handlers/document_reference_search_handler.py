import json

import boto3
from boto3.dynamodb.conditions import Key
import logging
from botocore.exceptions import ClientError

from services.dynamo_query_service import DynamoQueryService
from utils.exceptions import InvalidResourceIdException
from utils.lambda_response import ApiGatewayResponse
from utils.nhs_number_validator import validate_id

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Constants
TABLE_NAME = "dev_DocumentReferenceMetadata"


def lambda_handler(event, context):
    try:
        nhs_number = event["queryStringParameters"]["patientId"]
        validate_id(nhs_number)
    except InvalidResourceIdException:
        return ApiGatewayResponse(400, "Invalid NHS number", "GET")

    try:
        response = DynamoQueryService(TABLE_NAME)(nhs_number, "Created, FileName")
    except ClientError:
        return ApiGatewayResponse(500, "error", "GET")

    if response is not None and 'Items' in response:
        results = response['Items']
    else:
        logger.error(f"Unrecognised response from DynamoDB: {response!r}")
        return ApiGatewayResponse(500, "Unrecognised response from DynamoDB", "GET")

    return ApiGatewayResponse(200, results, "GET")

