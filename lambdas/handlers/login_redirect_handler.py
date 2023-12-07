from enums.logging_app_interaction import LoggingAppInteraction
from services.login_redirect_service import LoginRedirectService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.exceptions import LoginRedirectException
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = LoggingService(__name__)


@set_request_context_for_logging
@override_error_check
@ensure_environment_variables(names=["AUTH_DYNAMODB_NAME"])
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.LOGIN.value
    login_redirect_service = LoginRedirectService()
    try:
        location_header = login_redirect_service.prepare_redirect_response()
    except LoginRedirectException as e:
        logger.error(
            e.message, {"Result": f"Redirect unsuccessful due to {str(e.message)}"}
        )
        return ApiGatewayResponse(
            e.status_code, f"An error occurred due to: {str(e.message)}", "GET"
        ).create_api_gateway_response()
    return ApiGatewayResponse(303, "", "GET").create_api_gateway_response(
        headers=location_header
    )
