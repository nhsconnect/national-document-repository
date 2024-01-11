import json
from urllib.parse import parse_qs

from enums.logging_app_interaction import LoggingAppInteraction
from services.back_channel_logout_service import BackChannelLogoutService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.exceptions import LogoutFailureException
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = LoggingService(__name__)


@set_request_context_for_logging
@ensure_environment_variables(names=["OIDC_CALLBACK_URL", "AUTH_DYNAMODB_NAME"])
@override_error_check
@handle_lambda_exceptions
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.LOGOUT.value
    logger.info("Back channel logout handler triggered")

    back_channel_logout_service = BackChannelLogoutService()

    try:
        logger.info(f"incoming event {event}")
        body = parse_qs(event.get("body", None))
        if not body:
            raise LogoutFailureException(
                "An error occurred due to missing request body/logout token"
            )

        token = body.get("logout_token", [None])[0]

        if not token:
            raise LogoutFailureException(
                "An error occurred due to missing logout token"
            )

        back_channel_logout_service.logout_handler(token)

        return ApiGatewayResponse(200, "", "POST").create_api_gateway_response()
    except LogoutFailureException as e:
        logger.error(str(e), {"Result": "Unsuccessful logout"})
        return ApiGatewayResponse(
            400,
            json.dumps({"error": "failed logout", "error_description": str(e)}),
            "POST",
        ).create_api_gateway_response()
