from typing import Callable

from enums.lambda_error import LambdaError
from utils.audit_logging_setup import LoggingService
from utils.edge_response import EdgeResponse
from utils.error_response import ErrorResponse
from utils.lambda_exceptions import CloudFrontEdgeException
from utils.request_context import request_context

logger = LoggingService(__name__)


def handle_edge_exceptions(lambda_func: Callable):
    def interceptor(event, context):
        interaction_id = getattr(request_context, "request_id", None)
        try:
            return lambda_func(event, context)
        except CloudFrontEdgeException as e:
            logger.error(str(e))
            return EdgeResponse(
                status_code=e.status_code,
                body=ErrorResponse(e.err_code, e.message, interaction_id).create(),
                methods=event.get("httpMethod", "GET"),
            ).create_edge_response()
        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}")
            err_code = LambdaError.EdgeMalformed.value("err_code")
            message = LambdaError.EdgeMalformed.value("message")
            return EdgeResponse(
                status_code=500,
                body=ErrorResponse(err_code, message, interaction_id).create(),
                methods=event.get("httpMethod", "GET"),
            ).create_edge_response()

    return interceptor
