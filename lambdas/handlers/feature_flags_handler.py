import json

from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.lambda_response import ApiGatewayResponse

logger = LoggingService(__name__)


@set_request_context_for_logging
@ensure_environment_variables(
    names=["APPCONFIG_APPLICATION", "APPCONFIG_CONFIGURATION", "APPCONFIG_ENVIRONMENT"]
)
@handle_lambda_exceptions
@override_error_check
def lambda_handler(event, context):
    response = {
        "message": "Key error",
        "err_code": "FFL_5003",
        "interaction_id": "88888888-4444-4444-4444-121212121212",
    }

    return ApiGatewayResponse(
        500, json.dumps(response), "GET"
    ).create_api_gateway_response()
