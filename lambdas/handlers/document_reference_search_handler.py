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
    # Use ProjectionExpression for only getting the "D, Created and FileName fields
    # https://stackoverflow.com/questions/52994822/using-a-projectionexpression-with-reserved-words-with-boto3-in-dynamodb

def lambda_handler(event, context):
    try:
        dynamodb_client = boto3.client('dynamodb', region_name="eu-west-2")
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(TABLE_NAME)

        response = table.query(
            IndexName='NhsNumberIndex',
            KeyConditionExpression=Key('NhsNumber').eq('9449306621')
        )

        return ApiGatewayResponse(200, response['Items'], "GET")

    except ClientError as e:
        logger.error("Unable to connect to DB")
        logger.error(e)
