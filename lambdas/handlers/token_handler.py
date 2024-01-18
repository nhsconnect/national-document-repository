import json

from enums.logging_app_interaction import LoggingAppInteraction
from services.login_service import LoginService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.error_response import ErrorResponse, LambdaError
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
        auth_code = event["queryStringParameters"]["err_code"]
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
        error = LambdaError.LoginNoAuth.value
        msg = error["message"]
        err_code = error["err_code"]
        return ApiGatewayResponse(
            400,
            ErrorResponse(err_code, msg).create(),
            "GET",
        ).create_api_gateway_response()
