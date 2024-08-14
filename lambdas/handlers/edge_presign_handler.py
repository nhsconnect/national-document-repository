import json

from enums.logging_app_interaction import LoggingAppInteraction
from utils.audit_logging_setup import LoggingService
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.request_context import request_context

logger = LoggingService(__name__)


@set_request_context_for_logging
@override_error_check
@handle_lambda_exceptions
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.EDGE_PRESIGN.value
    logger.info("Edge Presign handler triggered")
    location_header = {"Location": "https://www.google.co.uk", "Hello": "World"}
    return json.loads(location_header)
