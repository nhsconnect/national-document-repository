import os

import boto3
import jwt
from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from enums.logging_app_interaction import LoggingAppInteraction
from services.base.dynamo_service import DynamoDBService
from utils.audit_logging_setup import LoggingService
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = LoggingService(__name__)


@set_request_context_for_logging
@override_error_check
@handle_lambda_exceptions
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.LOGOUT.value
    logger.info("Logout handler triggered")

    token = None
    headers = event.get("headers")
    if headers:
        token = headers["Authorization"]
    return logout_handler(token)


def logout_handler(token):
    try:
        ssm_public_key_parameter_name = os.environ["SSM_PARAM_JWT_TOKEN_PUBLIC_KEY"]
        ssm_response = get_ssm_parameter(key=ssm_public_key_parameter_name)
        jwt_class = jwt
        public_key = ssm_response["Parameter"]["Value"]
        logger.info("decoding token")
        decoded_token = decode_token(jwt_class=jwt_class, token=token, key=public_key)
        session_id = decoded_token["ndr_session_id"]
        remove_session_from_dynamo_db(session_id)

    except ClientError as e:
        logger.error(
            f"{LambdaError.LogoutClient.to_str()}: {e}",
            {"Result": "Unsuccessful logout"},
        )
        return ApiGatewayResponse(
            500,
            LambdaError.LogoutClient.create_error_body(),
            "GET",
        ).create_api_gateway_response()
    except (jwt.PyJWTError, KeyError) as e:
        logger.error(
            f"{LambdaError.LogoutDecode.to_str()}: {e}",
            {"Result": "Unsuccessful logout"},
        )
        return ApiGatewayResponse(
            400, LambdaError.LogoutDecode.create_error_body(), "GET"
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
