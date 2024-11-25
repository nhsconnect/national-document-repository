import json

import requests
from enums.mns_notification_types import MNSNotificationTypes
from models.mns_sqs_message import MNSSQSMessage
from services.process_mns_message_service import MNSNotificationService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging

logger = LoggingService(__name__)


@set_request_context_for_logging
@ensure_environment_variables(
    names=[
        "APPCONFIG_CONFIGURATION",
        "APPCONFIG_ENVIRONMENT",
        "LLOYD_GEORGE_DYNAMODB_NAME",
    ]
)
@override_error_check
@handle_lambda_exceptions
def lambda_handler(event, context):
    logger.info(f"Received MNS notification event: {event}")

    sqs_messages = event.get("Records", [])

    for sqs_message in sqs_messages:
        try:
            sqs_message = json.loads(sqs_message["body"])

            if sqs_message["type"] == MNSNotificationTypes.SUBSCRIPTION:
                handle_subscription(sqs_message)
                continue

            mns_message = MNSSQSMessage(**sqs_message)
            MNSSQSMessage.model_validate(mns_message)
            if mns_message.type in MNSNotificationTypes.__members__.values():

                notification_service = MNSNotificationService()
                notification_service.handle_mns_notification(mns_message)

            continue
        except Exception as error:
            logger.error(f"Error processing SQS message: {error}.")
            logger.info("Continuing to next message.")


def handle_subscription(message):
    try:
        url = message["SubscribeURL"]
        response = requests.get(url)
        response.raise_for_status()
    except Exception as error:
        logger.error(f"Error processing subscription request: {error}.")
