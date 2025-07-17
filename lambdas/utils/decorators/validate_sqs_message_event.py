from typing import Callable

from enums.lambda_error import LambdaError
from utils.audit_logging_setup import LoggingService
from utils.lambda_response import ApiGatewayResponse

logger = LoggingService(__name__)


def validate_sqs_event(lambda_func: Callable):
    """A decorator for lambda handler.
    Verify that the incoming sqs message event contains a valid and usable array of message records.
    If not, returns a 400 Bad request response before actual lambda was triggered.

    Usage:
    @validate_sqs_message
    def lambda_handler(event, context):
        ...
    """

    def interceptor(event, context):
        sqs_records = event.get("Records")
        if not sqs_records or len(sqs_records) < 1:
            logger.info(f"No SQS messages found in event: {event}")
            return ApiGatewayResponse(
                status_code=400,
                body=LambdaError.SqsInvalidEvent.create_error_body(),
                methods="GET",
            ).create_api_gateway_response()

        return lambda_func(event, context)

    return interceptor
