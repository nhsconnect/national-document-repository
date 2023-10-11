import logging
import os

import boto3
import jwt
from botocore.exceptions import ClientError
from lambdas.services.ssm_service import get_ssm_parameter
from services.dynamo_service import DynamoDBService
from utils.lambda_response import ApiGatewayResponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    token = event["headers"]["x-auth"]
    return logout_handler(token)


def logout_handler(token):
    try:
        ssm_response = get_ssm_parameter("SSM_PARAM_JWT_TOKEN_PUBLIC_KEY")
        public_key = ssm_response["Parameter"]["Value"]
        
        logger.info("decoding token")
        decoded_token = jwt.decode(token, public_key, algorithms=["RS256"])
        session_id = decoded_token["ndr_session_id"]
        remove_session_from_dynamo_db(session_id)

    except ClientError as e:
        logger.error(f"Error logging out user: {e}")
        return ApiGatewayResponse(
            500, "Error logging user out", "GET"
        ).create_api_gateway_response()
    except (jwt.PyJWTError, KeyError) as e:
        logger.error(f"error while decoding JWT: {e}")
        return ApiGatewayResponse(
            400, "Invalid x-auth header", "GET"
        ).create_api_gateway_response()
    return ApiGatewayResponse(200, "", "GET").create_api_gateway_response()


def remove_session_from_dynamo_db(session_id):
    logger.info(f"Session to be removed: {session_id}")
    dynamodb_name = os.environ["AUTH_DYNAMODB_NAME"]
    dynamodb_service = DynamoDBService()
    dynamodb_service.delete_item(
        key={"NDRSessionId": session_id}, table_name=dynamodb_name
    )
