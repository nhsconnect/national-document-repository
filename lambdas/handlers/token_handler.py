import json
import os
import time
import uuid

import jwt
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from enums.logging_app_interaction import LoggingAppInteraction
from enums.repository_role import RepositoryRole
from models.oidc_models import IdTokenClaimSet
from services.dynamo_service import DynamoDBService
from services.login_service import LoginService
from services.token_handler_ssm_service import TokenHandlerSSMService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.exceptions import (
    AuthorisationException,
    OrganisationNotFoundException,
    TooManyOrgsException,
)
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = LoggingService(__name__)

token_handler_ssm_service = TokenHandlerSSMService()
login_service = LoginService()


@set_request_context_for_logging
@override_error_check
@ensure_environment_variables(
    names=["AUTH_STATE_TABLE_NAME", "AUTH_SESSION_TABLE_NAME"]
)
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.LOGIN.value

    try:
        missing_value_response_body = (
            "No auth code and/or state in the query string parameters"
        )
        auth_code = event["queryStringParameters"]["code"]
        state = event["queryStringParameters"]["state"]
        if not (auth_code and state):
            return respond_with(400, missing_value_response_body)
    except (KeyError, TypeError):
        return respond_with(400, missing_value_response_body)

    try:
        #call service
        repository_role, authorisation_token = login_service.exchange_token(state, auth_code)


        logger.info("Creating response")
        response = {
            "role": repository_role.value,
            "authorisation_token": authorisation_token,
        }

        logger.audit_splunk_info(
            "User logged in successfully", {"Result": "Successful login"}
        )
        return respond_with(200, json.dumps(response))

    except AuthorisationException as error:
        logger.error(error, {"Result": "Unauthorised"})
        return respond_with(401, "Failed to authenticate user with OIDC service")
    except (ClientError, KeyError, TypeError) as error:
        logger.error(error, {"Result": "Unauthorised"})
        return respond_with(500, "Server error")
    except jwt.PyJWTError as error:
        logger.info(f"error while encoding JWT: {error}", {"Result": "Unauthorised"})
        return respond_with(500, "Server error")
    except OrganisationNotFoundException as error:
        logger.info(
            f"Organisation does not exist for given ODS code: {error}",
            {"Result": "Unauthorised"},
        )
        return respond_with(500, "Organisation does not exist for given ODS code")
    except TooManyOrgsException:
        return respond_with(500, "No single organisation found for given ods codes")


def respond_with(http_status_code, body):
    return ApiGatewayResponse(
        http_status_code, body, "GET"
    ).create_api_gateway_response()
