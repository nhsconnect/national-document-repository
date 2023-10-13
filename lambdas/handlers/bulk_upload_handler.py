import logging

from services.bulk_upload_service import BulkUploadService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, _context):
    logger.info("Received event. Starting bulk upload process")
    bulk_upload_service = BulkUploadService()

    if "Records" not in event:
        logger.error(f"No sqs messages found in event: {event}. Will ignore this event")
        return

    for index, message in enumerate(event["Records"], start=1):
        logger.info(f"Processing message {index} of {len(event['Records'])}")
        bulk_upload_service.handle_sqs_message(message)
