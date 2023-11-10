import os

import boto3
import jwt
from botocore.exceptions import ClientError

from enums.logging_app_interaction import LoggingAppInteraction
from services.dynamo_service import DynamoDBService
from utils.audit_logging_setup import LoggingService
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = LoggingService(__name__)


@set_request_context_for_logging
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.LOGOUT.value
    return logout_handler()


def logout_handler():
    try:
        if request_context.authorization is None:
            raise jwt.PyJWTError
        session_id = request_context.authorization["ndr_session_id"]
        remove_session_from_dynamo_db(session_id)

    except ClientError as e:
        logger.error(f"Error logging out user: {e}", {"Result": "Unsuccessful logout"})
        return ApiGatewayResponse(
            500, "Error logging user out", "GET"
        ).create_api_gateway_response()
    except (jwt.PyJWTError, KeyError) as e:
        logger.error(
            f"error while decoding JWT: {e}", {"Result": "Unsuccessful logout"}
        )
        return ApiGatewayResponse(
            400, "Invalid x-auth header", "GET"
        ).create_api_gateway_response()
    return ApiGatewayResponse(200, "", "GET").create_api_gateway_response()


def get_ssm_parameter(key):
    client = boto3.client("ssm", region_name="eu-west-2")
    ssm_response = client.get_parameter(Name=key, WithDecryption=True)
    return ssm_response


def decode_token(jwt_class, token, key):
    return jwt_class.decode(token, key, algorithms=["RS256"])


def remove_session_from_dynamo_db(session_id):
    dynamodb_name = os.environ["AUTH_DYNAMODB_NAME"]
    dynamodb_service = DynamoDBService()
    dynamodb_service.delete_item(
        key={"NDRSessionId": session_id}, table_name=dynamodb_name
    )
    logger.info(f"Session removed: {session_id}", {"Result": "Successful logout"})
