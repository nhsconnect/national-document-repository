from enums.feature_flags import FeatureFlags
from services.feature_flags_service import FeatureFlagService
from services.process_nems_message_service import ProcessNemsMessageService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.lambda_response import ApiGatewayResponse

logger = LoggingService(__name__)


@set_request_context_for_logging
@ensure_environment_variables(
    names=[
        "APPCONFIG_APPLICATION",
        "APPCONFIG_CONFIGURATION",
        "APPCONFIG_ENVIRONMENT",
        "LLOYD_GEORGE_DYNAMODB_NAME",
    ]
)
@override_error_check
def lambda_handler(event, context):
    logger.info(f"Received event: {event}")

    feature_flag_service = FeatureFlagService()
    nems_flag_name = FeatureFlags.NEMS_ENABLED.value
    nems_enabled_flag_object = feature_flag_service.get_feature_flags_by_flag(
        nems_flag_name
    )

    if not nems_enabled_flag_object[nems_flag_name]:
        logger.info("Feature flag not enabled, event will not be processed")
        return

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
