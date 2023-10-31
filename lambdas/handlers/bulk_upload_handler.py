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
        try:
            logger.info(f"Processing message {index} of {len(event['Records'])}")
            bulk_upload_service.handle_sqs_message(message)
        except Exception as error:
            logger.info(f"Fail to process current message due to error: {error}")
            logger.info("Continue on next message")
    logger.info(f"Finished processing all {len(event['Records'])} messages")
