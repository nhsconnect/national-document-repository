from typing import Callable

from enums.lambda_error import LambdaError
from utils.audit_logging_setup import LoggingService
from utils.lambda_response import ApiGatewayResponse

logger = LoggingService(__name__)


def validate_dynamo_stream(lambda_func: Callable):
    """A decorator for lambda handler.
    Verify that the incoming dynamo stream event contains a valid event type and usable image.
    If not, returns a 400 Bad request response before actual lambda was triggered.

    Usage:
    @validate_dynamo_stream_event
    def lambda_handler(event, context):
        ...
    """

    def interceptor(event, context):
        dynamo_records = event.get("Records")

        if not dynamo_records:
            logger.error("Received an empty stream event from DynamoDb")
            return ApiGatewayResponse(
                400,
                LambdaError.DynamoInvalidStreamEvent.create_error_body(),
                event.get("httpMethod", "GET"),
            ).create_api_gateway_response()

        for record in dynamo_records:
            dynamo_event = record.get("dynamodb", {})
            event_name = record.get("eventName")
            if not dynamo_event or not event_name:
                logger.error(
                    "Failed to extract dynamo event details from DynamoDb stream"
                )
                return ApiGatewayResponse(
                    400,
                    LambdaError.DynamoInvalidStreamEvent.create_error_body(),
                    event.get("httpMethod", "GET"),
                ).create_api_gateway_response()

        return lambda_func(event, context)

    return interceptor
