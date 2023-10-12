import json
import logging
import os

from services.bulk_upload_service import BulkUploadService
from services.lloyd_george_validator import LGInvalidFilesException
from services.sqs_service import SQSService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, _context):
    logger.info("Received event. Starting bulk upload process")
    bulk_upload_service = BulkUploadService()
    for index, message in enumerate(event["Records"], start=1):
        try:
            logger.info(f"Processing message {index} of {len(event['Records'])}")
            bulk_upload_service.handle_sqs_message(message)
            logger.info("Completed file upload for current message")
        except LGInvalidFilesException as e:
            send_to_invalid_queue(message, str(e))
        except Exception as e:
            logger.error(e)
            raise e


def send_to_invalid_queue(message: dict, error_message=None):
    sqs_service = SQSService()
    invalid_queue_url = os.environ["INVALID_SQS_QUEUE_URL"]
    if error_message:
        message["error_message"] = error_message

    sqs_service.send_message(
        queue_url=invalid_queue_url, message_body=json.dumps(message)
    )
    logger.info(f"sent message to invalid queue: {message}")
