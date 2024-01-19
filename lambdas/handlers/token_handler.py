import json

from enums.lambda_error import LambdaError
from enums.logging_app_interaction import LoggingAppInteraction
from services.login_service import LoginService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.lambda_exceptions import LoginException
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = LoggingService(__name__)


@set_request_context_for_logging
@override_error_check
@ensure_environment_variables(
    names=["AUTH_STATE_TABLE_NAME", "AUTH_SESSION_TABLE_NAME"]
)
@handle_lambda_exceptions
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.LOGIN.value
    logger.info("Token request handler triggered")

    try:
        auth_code = event["queryStringParameters"]["code"]
        state = event["queryStringParameters"]["state"]
        if not (auth_code and state):
            raise LoginException(400, LambdaError.LoginNoState)

        login_service = LoginService()

        response = login_service.generate_session(state, auth_code)
        logger.audit_splunk_info(
            "User logged in successfully", {"Result": "Successful login"}
        )
        return ApiGatewayResponse(
            200, json.dumps(response), "GET"
        ).create_api_gateway_response()

    except (KeyError, TypeError):
        logger.error(
            f"{ LambdaError.LoginNoAuth.to_str()}", {"Result": "Unsuccessful login"}
        )
        return ApiGatewayResponse(
            400,
            LambdaError.LoginNoAuth.create_error_body(),
            "GET",
        ).create_api_gateway_response()
