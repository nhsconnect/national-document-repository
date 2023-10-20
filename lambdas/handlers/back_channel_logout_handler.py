import json
import logging
import os
from botocore.exceptions import ClientError
from services.oidc_service import OidcService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.exceptions import AuthorisationException
from services.dynamo_service import DynamoDBService
from utils.lambda_response import ApiGatewayResponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@ensure_environment_variables(
    names=["OIDC_CALLBACK_URL", "AUTH_DYNAMODB_NAME"]
)
def lambda_handler(event, context):
    logger.info(f"event = {event}")
    try:
        body = json.loads(event["body"])
        token = body["logout_token"]
    except KeyError as e:
        return ApiGatewayResponse(400, f"An error occurred due to missing key: {str(e)}",
                                  "POST").create_api_gateway_response()
    return logout_handler(token)


def logout_handler(token):
    try:
        logger.info("decoding token")
        oidc_service = OidcService()
        decoded_token = oidc_service.validate_and_decode_token(token)
        session_id = decoded_token["sid"]
        remove_session_from_dynamo_db(session_id)

    except ClientError as e:
        logger.error(f"Error logging out user: {e}")
        return ApiGatewayResponse(
            500, """{ "error":"Internal error logging user out"}""", "POST"
        ).create_api_gateway_response()
    except AuthorisationException as e:
        logger.error(f"error while decoding JWT: {e}")
        return ApiGatewayResponse(
            400, """{ "error":"JWT was invalid"}""", "POST"
        ).create_api_gateway_response()
    except KeyError as e:
        logger.error(f"No field 'sid' in decoded token: {e}")
        return ApiGatewayResponse(
            400, """{ "error":"No sid field in decoded token"}""", "POST"
        ).create_api_gateway_response()

    return ApiGatewayResponse(200, "", "POST").create_api_gateway_response()


def remove_session_from_dynamo_db(session_id):
    logger.info(f"Session to be removed: {session_id}")
    dynamodb_name = os.environ["AUTH_DYNAMODB_NAME"]
    dynamodb_service = DynamoDBService()
    dynamodb_service.delete_item(
        key={"NDRSessionId": session_id}, table_name=dynamodb_name
    )
