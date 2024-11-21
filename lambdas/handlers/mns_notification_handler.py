import json

from models.mns_sqs_message import MNSSQSMessage
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
        # might not need the name of the queue, as this is what is trigging the lamdba
    ]
)
# need to check what this does
@override_error_check
@handle_lambda_exceptions
def lambda_handler(event, context):
    logger.info(f"Received MNS notification event: {event}")

    sqs_messages = event.get("Records", [])

    for sqs_message in sqs_messages:
        try:
            sqs_message = json.loads(sqs_message["body"])
            # event_type = sqs_message["type"]
            # nhs_number = sqs_message["subject"]["nhsNumber"]
            mns_message = MNSSQSMessage(**sqs_message)
            MNSSQSMessage.model_validate(mns_message)

            return mns_message.subject.nhs_number
        except Exception as error:
            logger.error(f"Error processing SQS message: {error}.")
            logger.info("Continuing to next message.")
            pass

    # how do we want to handle empty messages, bulk up load
    # if "Records" not in event or len(event["Records"]) < 1:
    #     http_status_code = 400
    #     response_body = f"No sqs messages found in event: {event}. Event ignored."
    #     logger.error(response_body, {"Result": "Did not process MNS notification."})
    #     return ApiGatewayResponse(
    #         status_code=http_status_code, body=response_body, methods="GET"
    #     )
