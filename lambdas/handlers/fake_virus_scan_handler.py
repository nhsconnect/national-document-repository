import logging
import os

import boto3
from botocore.exceptions import ClientError

from services.dynamo_service import DynamoDBService
from utils.lambda_response import ApiGatewayResponse


def lambda_handler(event, context):
    document_store_table_name = os.environ["DOCUMENT_STORE_DYNAMODB_NAME"]
    records = event["Records"]
    dynamo_service = DynamoDBService()

    for record in records:
        key = record["s3"]["object"]["key"]

        try:
            dynamo_service.update_item_service(
                table_name=document_store_table_name,
                key={'ID': key},
                update_expression="set VirusScannerResult = :r",
                expression_attribute_values={
                    ':r': 'Clean',
                },
            )
            logging.info(f"File ID {key} in table {document_store_table_name} marked as CLEAN")
        except ClientError:
            return ApiGatewayResponse(500, "Unable to mark file as clean", "UPDATE").create_api_gateway_response()

        return ApiGatewayResponse(200, "File marked as Clean", "UPDATE").create_api_gateway_response()

