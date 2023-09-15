import logging
import os

import boto3
from botocore.exceptions import ClientError

from lambdas.services.dynamo_services import DynamoDBService
from lambdas.utils.lambda_response import ApiGatewayResponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context, jwt=None):
    try:
        ssm_public_key_parameter_name = os.environ["SSM_PARAM_JWT_TOKEN_PUBLIC_KEY"]
        token = event['authorizationToken']
        client = boto3.client("ssm", region_name="eu-west-2")
        ssm_response = client.get_parameter(
        Name=ssm_public_key_parameter_name, WithDecryption=True
        )
        public_key = ssm_response["Parameter"]["Value"]
        decoded = jwt.decode(
            event["authorizationToken"], public_key, algorithms=["RS256"]
        )
        session_id = decoded["ndr_session_id"]

        dynamodb_name = os.environ["AUTH_DYNAMODB_NAME"]
        dynamodb_service = DynamoDBService(dynamodb_name)
        dynamodb_service.update_item_service(
            key={

            }
        )

    except ClientError as e:
        logger.error(f"Error getting using aws client: {e}")
        return ApiGatewayResponse(500, e, "GET").create_api_gateway_response()

    return ApiGatewayResponse(302, "", "GET").create_api_gateway_response()