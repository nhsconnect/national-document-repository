from typing import Callable

from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from utils.audit_logging_setup import LoggingService
from utils.error_response import ErrorResponse
from utils.lambda_exceptions import LambdaException
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

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

            interaction_id = getattr(request_context, "request_id", None)
            return ApiGatewayResponse(
                status_code=e.status_code,
                body=ErrorResponse(e.err_code, e.message, interaction_id).create(),
                methods=event.get("httpMethod", "GET"),
            ).create_api_gateway_response()
        except ClientError as e:
            logger.error(
                f"{LambdaError.GatewayError.to_str()}: {str(e)}",
                {"Result": "Failed to utilise AWS client/resource"},
            )
            return ApiGatewayResponse(
                status_code=500,
                body=LambdaError.GatewayError.create_error_body(),
                methods=event.get("httpMethod", "GET"),
            ).create_api_gateway_response()
        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}", exc_info=True)

            interaction_id = getattr(request_context, "request_id", None)
            return ApiGatewayResponse(
                status_code=500,
                body=ErrorResponse("InternalServerError", "An internal server error occurred", interaction_id).create(),
                methods=event.get("httpMethod", "GET"),
            ).create_api_gateway_response()

    return interceptor
