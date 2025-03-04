import json

from enums.mns_notification_types import MNSNotificationTypes
from models.mns_sqs_message import MNSSQSMessage
from pydantic_core._pydantic_core import ValidationError
from services.process_mns_message_service import MNSNotificationService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.request_context import request_context

logger = LoggingService(__name__)


@set_request_context_for_logging
@ensure_environment_variables(
    names=[
        "APPCONFIG_CONFIGURATION",
        "APPCONFIG_ENVIRONMENT",
        "LLOYD_GEORGE_DYNAMODB_NAME",
        "MNS_NOTIFICATION_QUEUE_URL",
    ]
)
def lambda_handler(event, context):
    logger.info(f"Received MNS notification event: {event}")
    notification_service = MNSNotificationService()
    sqs_messages = event.get("Records", [])

    for sqs_message in sqs_messages:
        try:
            sqs_message = json.loads(sqs_message["body"])

            mns_message = MNSSQSMessage(**sqs_message)
            MNSSQSMessage.model_validate(mns_message)

            request_context.patient_nhs_no = mns_message.subject.nhs_number
            logger.info(
                f"Processing SQS message for nhs number: {mns_message.subject.nhs_number}"
            )

            if mns_message.type in MNSNotificationTypes.__members__.values():
                notification_service.handle_mns_notification(mns_message)

        except ValidationError as error:
            logger.error("Malformed MNS notification message")
            logger.error(error)
            raise error
        except Exception as error:
            logger.error(f"Error processing SQS message: {error}.")
            raise error
        logger.info("Continuing to next message.")
