from typing import Callable

from utils.audit_logging_setup import LoggingService
from utils.edge_response import EdgeResponse
from utils.error_response import ErrorResponse
from utils.lambda_exceptions import LambdaException
from utils.request_context import request_context

logger = LoggingService(__name__)


def handle_edge_exceptions(lambda_func: Callable):
    """A decorator for lambda edge handler.
    Catch custom Edge Exceptions or AWS ClientError that may be unhandled or raised

    Usage:
    @handle_edge_exceptions
    def lambda_handler(event, context):
        ...
    """

    def interceptor(event, context):
        try:
            return lambda_func(event, context)
        except LambdaException as e:
            logger.error(str(e))

            interaction_id = getattr(request_context, "request_id", None)
            return EdgeResponse(
                status_code=e.status_code,
                body=ErrorResponse(e.err_code, e.message, interaction_id).create(),
                methods=event.get("httpMethod", "GET"),
            ).create_edge_response()

    return interceptor
