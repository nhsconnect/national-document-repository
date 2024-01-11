from typing import Callable

from botocore.exceptions import ClientError
from utils.audit_logging_setup import LoggingService
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
            return ApiGatewayResponse(
                status_code=e.status_code,
                err_code=e.err_code,
                body=e.message,
                methods=event.get("httpMethod", "GET"),
            ).create_api_gateway_response()
        except ClientError as e:
            logger.error(str(e), {"Result": "Failed to utilise AWS client/resource"})
            return ApiGatewayResponse(
                status_code=500,
                err_code="ERR_AWS_CLIENT",
                body="Failed to utilise AWS client/resource",
                methods=event.get("httpMethod", "GET"),
            ).create_api_gateway_response()

    return interceptor
