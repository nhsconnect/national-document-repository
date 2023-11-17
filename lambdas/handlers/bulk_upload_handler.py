from botocore.exceptions import ClientError
from services.bulk_upload_service import BulkUploadService
from utils.audit_logging_setup import LoggingService
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.exceptions import InvalidMessageException
from utils.lloyd_george_validator import LGInvalidFilesException
from utils.decorators.override_error_check import override_error_check

logger = LoggingService(__name__)


@set_request_context_for_logging
@override_error_check
def lambda_handler(event, _context):
    logger.info("Received event. Starting bulk upload process")
    bulk_upload_service = BulkUploadService()

    if "Records" not in event:
        logger.error(f"No sqs messages found in event: {event}. Will ignore this event")
        return

    for index, message in enumerate(event["Records"], start=1):
        try:
            logger.info(f"Processing message {index} of {len(event['Records'])}")
            bulk_upload_service.handle_sqs_message(message)
        except (
            ClientError,
            InvalidMessageException,
            LGInvalidFilesException,
            KeyError,
            TypeError,
            AttributeError,
        ) as error:
            logger.info(f"Fail to process current message due to error: {error}")
            logger.info("Continue on next message")
    logger.info(f"Finished processing all {len(event['Records'])} messages")
