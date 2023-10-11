import logging

from services.bulk_upload_service import BulkUploadService

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
        except RuntimeError:
            send_to_invalid_queue(message)
        except Exception as e:
            logger.error(e)
            raise e


def send_to_invalid_queue(message):
    logger.log(f"send message to invalid queue: {message}")
