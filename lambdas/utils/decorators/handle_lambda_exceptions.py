from typing import Callable

from botocore.exceptions import ClientError
from utils.audit_logging_setup import LoggingService
from utils.error_response import ErrorResponse
from utils.lambda_exceptions import LambdaException
from utils.lambda_response import ApiGatewayResponse

logger = LoggingService(__name__)


def handle_lambda_exceptions(lambda_func: Callable):
    """A decorator for lambda handler.
    Catch custom Lambda Exceptions or AWS ClientError that may be unhandled or raised

    Usage:
    @handle_lambda_exceptions
    def lambda_handler(event, context):
        ...
    """

    def interceptor(event, context):
        try:
            return lambda_func(event, context)
        except LambdaException as e:
            logger.error(str(e))
            return ApiGatewayResponse(
                status_code=e.status_code,
                body=ErrorResponse(e.message, e.err_code).create(),
                methods=event.get("httpMethod", "GET"),
            ).create_api_gateway_response()
        except ClientError as e:
            logger.error(str(e), {"Result": "Failed to utilise AWS client/resource"})
            return ApiGatewayResponse(
                status_code=500,
                body=ErrorResponse(
                    "Failed to utilise AWS client/resource", "GWY_5001"
                ).create(),
                methods=event.get("httpMethod", "GET"),
            ).create_api_gateway_response()

    return interceptor
