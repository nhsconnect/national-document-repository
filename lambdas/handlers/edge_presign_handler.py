import json

from enums.logging_app_interaction import LoggingAppInteraction
from utils.audit_logging_setup import LoggingService
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = LoggingService(__name__)


@override_error_check
@handle_lambda_exceptions
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.EDGE_PRESIGN.value
    logger.info("Edge Presign handler triggered")
    location_header = {"Location": "https://www.google.co.uk", "Hello": "World"}
    return ApiGatewayResponse(
        200, json.dumps(location_header), "GET"
    ).create_api_gateway_response()
