from services.process_nems_message_service import ProcessNemsMessageService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.lambda_response import ApiGatewayResponse

logger = LoggingService(__name__)


@set_request_context_for_logging
@override_error_check
@ensure_environment_variables(["LLOYD_GEORGE_DYNAMODB_NAME"])
def lambda_handler(event, context):
    logger.info(f"Received event: {event}")
    if "Records" not in event or len(event["Records"]) < 1:
        http_status_code = 400
        response_body = (
            f"No sqs messages found in event: {event}. Will ignore this event"
        )
        logger.error(response_body, {"Result": "Process nems message failed"})
        return ApiGatewayResponse(
            status_code=http_status_code, body=response_body, methods="GET"
        ).create_api_gateway_response()
    else:
        sqs_batch_response = {}
        process_nems_message_service = ProcessNemsMessageService()
        batch_item_failures = process_nems_message_service.process_messages_from_event(
            event["Records"]
        )
        sqs_batch_response["batchItemFailures"] = batch_item_failures
        return sqs_batch_response
