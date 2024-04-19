import json

from enums.logging_app_interaction import LoggingAppInteraction
from services.feature_flags_service import FeatureFlagService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = LoggingService(__name__)


@set_request_context_for_logging
@ensure_environment_variables(
    names=["APPCONFIG_APPLICATION", "APPCONFIG_CONFIGURATION", "APPCONFIG_ENVIRONMENT"]
)
@handle_lambda_exceptions
@override_error_check
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.FEATURE_FLAGS.value
    logger.info("Starting feature flag retrieval process")

    query_string_params = event.get("queryStringParameters")
    feature_flag_service = FeatureFlagService()

    if query_string_params and "flagName" in query_string_params:
        flag_name = query_string_params["flagName"]
        response = feature_flag_service.get_feature_flags_by_flag(flag_name)
    else:
        response = feature_flag_service.get_feature_flags()

    return ApiGatewayResponse(
        200, json.dumps(response), "GET"
    ).create_api_gateway_response()
