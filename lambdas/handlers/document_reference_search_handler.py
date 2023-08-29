import json

import boto3
from boto3.dynamodb.conditions import Key
import logging
from botocore.exceptions import ClientError

from utils.lambda_response import ApiGatewayResponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Constants
TABLE_NAME = "dev_DocumentReferenceMetadata"


def lambda_handler(event, context):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(TABLE_NAME)

        response = table.query(
            IndexName='NhsNumberIndex',
            KeyConditionExpression=Key('NhsNumber').eq('9449306621'),
            ProjectionExpression="Created, FileName"
        )

        if response is not None and 'Items' in response:
            results = response['Items']
        else:
            logger.warning(f"Unrecognised response from DynamoDB: {response!r}")
            return ApiGatewayResponse(500, "Unrecognised response from DynamoDB", "GET")

        return ApiGatewayResponse(200, results, "GET")

    except ClientError as e:
        logger.error("Unable to connect to DB")
        logger.error(e)
        return ApiGatewayResponse(500, "error", "GET")
