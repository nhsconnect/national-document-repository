from typing import Callable

from utils.lambda_exceptions import LambdaException
from utils.lambda_response import ApiGatewayResponse


def handle_lambda_exceptions(lambda_func: Callable):
    """A decorator for lambda handler.
    Catch our custom LambdaException and return an API gateway response according to the exception

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
                e.status_code, e.message, event.get("httpMethod", "GET")
            ).create_api_gateway_response()

    return interceptor
