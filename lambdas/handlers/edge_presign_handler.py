import json

from enums.logging_app_interaction import LoggingAppInteraction
from utils.audit_logging_setup import LoggingService
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.request_context import request_context

logger = LoggingService(__name__)


@override_error_check
@handle_lambda_exceptions
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.EDGE_PRESIGN.value
    logger.info(json.dumps(event))
    response = {
        "status": "302",  # Redirect status code
        "statusDescription": "Found",
        "headers": {
            "location": [{"key": "Location", "value": "https://www.google.co.uk"}],
            "hello": [{"key": "Hello", "value": "World"}],
        },
    }

    return response
