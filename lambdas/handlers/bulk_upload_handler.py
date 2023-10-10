import logging

from models.staging_metadata import StagingMetadata

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    for message in event["Records"]:
        handle_sqs_message(message)


def handle_sqs_message(message: dict):
    if message["eventSource"] != "aws:sqs":
        logger.info("Rejecting event as not coming from sqs")
        return

    staging_metadata_json = message["body"]
    staging_metadata = StagingMetadata.model_validate_json(staging_metadata_json)
    print(f"Got data for patient: {staging_metadata.nhs_number}")
