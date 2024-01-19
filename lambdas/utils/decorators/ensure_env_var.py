import os
from typing import Callable

from enums.lambda_error import LambdaError
from utils.audit_logging_setup import LoggingService
from utils.lambda_response import ApiGatewayResponse

logger = LoggingService(__name__)


def ensure_environment_variables(names: list[str]) -> Callable:
    """A decorator for lambda handler.
    Verify that the lambda environment got a set of specific environment variables.
    If not, returns a 500 Internal server error response and log the missing env var.

    Usage:
    @ensure_environment_variables(names=["LLOYD_GEORGE_BUCKET_NAME", "LLOYD_GEORGE_DYNAMODB_NAME"])
    def lambda_handler(event, context):
        ...
    """

    def wrapper(lambda_func: Callable):
        def interceptor(event, context):
            for name in names:
                if name not in os.environ:
                    logger.info(f"missing env var: '{name}'")
                    error_body = LambdaError.EnvMissing.create_error_body(
                        {"name": name}
                    )
                    return ApiGatewayResponse(
                        500, error_body, event["httpMethod"]
                    ).create_api_gateway_response()

            # Validation done. Return control flow to original lambda handler
            return lambda_func(event, context)

        return interceptor

    return wrapper
