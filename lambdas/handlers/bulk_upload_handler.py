import json
import logging
import os

from services.bulk_upload_service import BulkUploadService
from services.lloyd_george_validator import LGInvalidFilesException
from services.sqs_service import SQSService
from utils.exceptions import InvalidMessageException

logger = logging.getLogger()
logger.setLevel(logging.INFO)


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
        except (InvalidMessageException, LGInvalidFilesException) as error:
            handle_invalid_message(invalid_message=message, error=error)


def handle_invalid_message(invalid_message: dict, error=None):
    # Currently we just send the invalid message to invalid queue.
    # In future ticket, will change this to record errors in dynamo db
    invalid_queue_url = os.environ["INVALID_SQS_QUEUE_URL"]
    sqs_service = SQSService()

    new_message = {"original_message": invalid_message["body"]}
    if error:
        new_message["error"] = str(error)

    try:
        nhs_number = invalid_message["messageAttributes"]["NhsNumber"]["stringValue"]
    except KeyError:
        nhs_number = ""

    sqs_service.send_message_with_nhs_number_attr(
        queue_url=invalid_queue_url,
        message_body=json.dumps(new_message),
        nhs_number=nhs_number,
    )
    logger.info(f"Sent message to invalid queue: {invalid_message}")
