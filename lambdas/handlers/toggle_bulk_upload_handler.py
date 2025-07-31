import logging
import os

import boto3
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check

logger = logging.getLogger()
logger.setLevel(logging.INFO)

lambda_client = boto3.client("lambda")
ESM_UUID = os.environ["ESM_UUID"]


@override_error_check
@handle_lambda_exceptions
def lambda_handler(event, context):
    logger.info(f"Received event: {event}")

    action = event.get("action")
    if action not in ["enable", "disable"]:
        logger.error(f"Invalid action received: {action}")
        return {
            "statusCode": 400,
            "body": f"Invalid action. Must be 'enable' or 'disable', got: {action}",
        }

    try:
        lambda_client.update_event_source_mapping(
            UUID=ESM_UUID,
            Enabled=(action == "enable"),
        )

        logger.info(
            f"Successfully updated event source mapping {ESM_UUID}: Enabled={action == 'enable'}"
        )

        return {
            "statusCode": 200,
            "body": f"Event source mapping updated: Enabled={action == 'enable'}",
        }

    except Exception as e:
        logger.error(f"Failed to update event source mapping: {e}")
        return {
            "statusCode": 500,
            "body": f"Error updating event source mapping: {str(e)}",
        }
