from enums.lambda_error import LambdaError
from enums.logging_app_interaction import LoggingAppInteraction
from models.document_reference import DocumentReference
from pydantic.v1 import ValidationError
from services.document_deletion_service import DocumentDeletionService
from utils.audit_logging_setup import LoggingService
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.decorators.validate_dynamo_stream_event import validate_dynamo_stream
from utils.dynamo_utils import parse_dynamo_record
from utils.lambda_exceptions import DocumentDeletionServiceException
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = LoggingService(__name__)


@set_request_context_for_logging
@override_error_check
@handle_lambda_exceptions
@validate_dynamo_stream
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.DELETE_RECORD.value

    logger.info(
        "Delete Document Object handler has been triggered by DynamoDb REMOVE event"
    )
    try:
        event_record = event["Records"][0]

        event_type = event_record.get("eventName")
        deleted_dynamo_reference = event_record.get("dynamodb").get("OldImage", {})

        if event_type != "REMOVE" or not deleted_dynamo_reference:
            logger.error(
                "Failed to extract deleted record from DynamoDb stream",
                {"Results": "Failed to delete document"},
            )
            raise DocumentDeletionServiceException(
                400, LambdaError.DynamoInvalidStreamEvent
            )
        parsed_dynamo_record = parse_dynamo_record(deleted_dynamo_reference)
        document = DocumentReference.model_validate(parsed_dynamo_record)

        deletion_service = DocumentDeletionService()
        deletion_service.handle_object_delete(deleted_reference=document)
    except (ValueError, ValidationError) as e:
        logger.error(
            f"Failed to parse Document Reference from deleted record: {str(e)}",
            {"Results": "Failed to delete document"},
        )
        raise DocumentDeletionServiceException(
            400, LambdaError.DynamoInvalidStreamEvent
        )

    return ApiGatewayResponse(
        200, "Successfully deleted Document Reference object", "GET"
    ).create_api_gateway_response()
