import os
import time

import boto3
from botocore.exceptions import ClientError
from enums.logging_app_interaction import LoggingAppInteraction
from oauthlib.oauth2 import InsecureTransportError, WebApplicationClient
from services.dynamo_service import DynamoDBService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = LoggingService(__name__)


@set_request_context_for_logging
@override_error_check
@ensure_environment_variables(names=["AUTH_DYNAMODB_NAME"])
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.LOGIN.value
    return prepare_redirect_response(WebApplicationClient)


def prepare_redirect_response(web_application_client_class):
    try:
        ssm_response = get_ssm_parameters()

        oidc_parameters = {
            parameter["Name"]: parameter["Value"]
            for parameter in ssm_response["Parameters"]
        }

        oidc_client = web_application_client_class(
            client_id=oidc_parameters["OIDC_CLIENT_ID"],
        )

        url, _headers, _body = oidc_client.prepare_authorization_request(
            authorization_url=oidc_parameters["OIDC_AUTHORISE_URL"],
            redirect_url=os.environ["OIDC_CALLBACK_URL"],
            scope=[
                "openid",
                "profile",
                "nhsperson",
                "nationalrbacaccess",
                "selectedrole",
            ],
            prompt="login",
        )

        save_state_in_dynamo_db(oidc_client.state)
        location_header = {"Location": url}
        logger.info(
            "User was successfully redirected to CIS2",
            {"Result": "Successful redirect"},
        )

    except ClientError as e:
        logger.error(
            f"Error getting aws client: {e}", {"Result": "Unsuccessful redirect"}
        )
        return ApiGatewayResponse(
            500, "Server error", "GET"
        ).create_api_gateway_response()
    except InsecureTransportError as e:
        logger.error(
            f"Error preparing auth request: {e}", {"Result": "Unsuccessful redirect"}
        )
        return ApiGatewayResponse(
            500, "Server error", "GET"
        ).create_api_gateway_response()
    return ApiGatewayResponse(303, "", "GET").create_api_gateway_response(
        headers=location_header
    )


def save_state_in_dynamo_db(state):
    dynamodb_name = os.environ["AUTH_DYNAMODB_NAME"]
    dynamodb_service = DynamoDBService()
    ten_minutes = 60 * 10
    ttl = round(time.time()) + ten_minutes
    item = {"State": state, "TimeToExist": ttl}
    dynamodb_service.create_item(item=item, table_name=dynamodb_name)


def get_ssm_parameters():
    ssm_parameters_names = ["OIDC_AUTHORISE_URL", "OIDC_CLIENT_ID"]
    ssm_client = boto3.client("ssm")
    return ssm_client.get_parameters(Names=ssm_parameters_names)
