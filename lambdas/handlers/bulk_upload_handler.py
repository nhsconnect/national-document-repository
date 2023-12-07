from services.bulk_upload_service import BulkUploadService
from utils.audit_logging_setup import LoggingService
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.exceptions import BulkUploadException
from utils.lambda_response import ApiGatewayResponse

logger = LoggingService(__name__)


@set_request_context_for_logging
@override_error_check
def lambda_handler(event, _context):
    logger.info("Received event. Starting bulk upload process")

    http_status_code = 200
    response_body = f"Finished processing all {len(event['Records'])} messages"

    if "Records" not in event:
        http_status_code = 400
        response_body = f"No sqs messages found in event: {event}. Will ignore this event"
        logger.error(response_body)

    bulk_upload_service = BulkUploadService()

    try:
        bulk_upload_service.process_message_queue(event["Records"])
        logger.info(response_body)
    except BulkUploadException as error:
        http_status_code = 500
        response_body = f"Bulk upload failed with error: {error}"
        logger.error(response_body)

    return ApiGatewayResponse(status_code=http_status_code,
                              body=response_body,
                              methods="GET"
                              ).create_api_gateway_response()
