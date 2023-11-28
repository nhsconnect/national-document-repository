import os
from urllib.parse import parse_qs

from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from enums.logging_app_interaction import LoggingAppInteraction
from services.dynamo_service import DynamoDBService
from services.oidc_service import OidcService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.exceptions import AuthorisationException
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = LoggingService(__name__)


@set_request_context_for_logging
@ensure_environment_variables(names=["OIDC_CALLBACK_URL", "AUTH_DYNAMODB_NAME"])
@override_error_check
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.LOGOUT.value

    logger.info(f"incoming event {event}")
    try:
        body = parse_qs(event["body"])
        token = body["logout_token"][0]
    except (KeyError, IndexError) as e:
        logger.error(e)
        logger.error(
            f"An error occurred due to missing key: {str(e)}",
            {"Result": "Unsuccessful logout"},
        )
        return ApiGatewayResponse(
            400, f"An error occurred due to missing key: {str(e)}", "POST"
        ).create_api_gateway_response()
    return logout_handler(token)


def logout_handler(token):
    try:
        oidc_service = OidcService()
        decoded_token = oidc_service.validate_and_decode_token(token)
        sid = decoded_token["sid"]
        remove_session_from_dynamo_db(sid)

    except ClientError as e:
        logger.error(f"Error logging out user: {e}", {"Result": "Unsuccessful logout"})
        return ApiGatewayResponse(
            500, """{ "error":"Internal error logging user out"}""", "POST"
        ).create_api_gateway_response()
    except AuthorisationException as e:
        logger.error(
            f"error while decoding JWT: {e}", {"Result": "Unsuccessful logout"}
        )
        return ApiGatewayResponse(
            400, """{ "error":"JWT was invalid"}""", "POST"
        ).create_api_gateway_response()
    except KeyError as e:
        logger.error(
            f"No field 'sid' in decoded token: {e}", {"Result": "Unsuccessful logout"}
        )
        return ApiGatewayResponse(
            400, """{ "error":"No sid field in decoded token"}""", "POST"
        ).create_api_gateway_response()

    return ApiGatewayResponse(200, "", "POST").create_api_gateway_response()


def remove_session_from_dynamo_db(sid):
    dynamodb_name = os.environ["AUTH_DYNAMODB_NAME"]
    dynamodb_service = DynamoDBService()

    filter_sid = Attr("sid").eq(sid)
    db_response = dynamodb_service.scan_table(
        dynamodb_name, filter_expression=filter_sid
    )

    if "Items" in db_response:
        items = db_response["Items"]
        ndr_session_id = items[0]["NDRSessionId"]

        dynamodb_service.delete_item(
            key={"NDRSessionId": ndr_session_id}, table_name=dynamodb_name
        )

    logger.info(
        f"Session removed for sid: {sid} and NDRSessionId {ndr_session_id }",
        {"Result": "Successful logout"},
    )
