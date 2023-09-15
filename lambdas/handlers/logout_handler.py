import logging
import os

import boto3
from botocore.exceptions import ClientError

from lambdas.services.dynamo_services import DynamoDBService
from lambdas.utils.lambda_response import ApiGatewayResponse
import jwt


logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    token = event['authorizationToken']
    logout_handler(token)

def logout_handler(token):
    try:
        ssm_public_key_parameter_name = os.environ["SSM_PARAM_JWT_TOKEN_PUBLIC_KEY"]
        ssm_response = get_ssm_parameter(key = ssm_public_key_parameter_name)
        jwt_class = jwt
        public_key = ssm_response["Parameter"]["Value"]
        decoded_token = decode_token(jwt_class=jwt_class, token=token, key=public_key)
        session_id = decoded_token["ndr_session_id"]
        remove_session_from_dynamo_db(session_id)

    except ClientError as e:
        logger.error(f"Error getting using aws client: {e}")
        return ApiGatewayResponse(500, e, "GET").create_api_gateway_response()

    return ApiGatewayResponse(200, "", "GET").create_api_gateway_response()
def get_ssm_parameter(key):
    client = boto3.client("ssm", region_name="eu-west-2")
    ssm_response = client.get_parameter(
        Name=key, WithDecryption=True
    )
    return ssm_response

def decode_token(jwt_class, token, key):
    return jwt_class.decode(
        token, key, algorithms=["RS256"]
    )

def remove_session_from_dynamo_db(session_id):
    dynamodb_name = os.environ["AUTH_DYNAMODB_NAME"]
    dynamodb_service = DynamoDBService(dynamodb_name)
    dynamodb_service.delete_item_service(
        key={
            'NDRSessionID' : f"${session_id}"
        }
    )