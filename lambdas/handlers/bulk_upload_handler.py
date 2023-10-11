import logging

from services.bulk_upload_service import BulkUploadService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, _context):
    bulk_upload_service = BulkUploadService()
    for message in event["Records"]:
        try:
            bulk_upload_service.handle_sqs_message(message)
        except RuntimeError:
            send_to_invalid_queue(message)


def send_to_invalid_queue(message):
    logger.log(f"send message to invalid queue: {message}")
