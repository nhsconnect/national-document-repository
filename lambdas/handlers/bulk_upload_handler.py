import os

from enums.feature_flags import FeatureFlags
from services.bulk_upload_service import BulkUploadService
from services.feature_flags_service import FeatureFlagService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.exceptions import BulkUploadException
from utils.lambda_response import ApiGatewayResponse

logger = LoggingService(__name__)


@set_request_context_for_logging
@override_error_check
@ensure_environment_variables(names=["PDF_STITCHING_SQS_URL"])
@handle_lambda_exceptions
def lambda_handler(event, _context):
    logger.info("Received event. Starting bulk upload process")
    feature_flag_service = FeatureFlagService()
    validation_strict_mode_flag_object = feature_flag_service.get_feature_flags_by_flag(
        FeatureFlags.LLOYD_GEORGE_VALIDATION_STRICT_MODE_ENABLED.value
    )
    validation_strict_mode = validation_strict_mode_flag_object[
        FeatureFlags.LLOYD_GEORGE_VALIDATION_STRICT_MODE_ENABLED.value
    ]
    bypass_pds = os.getenv("BYPASS_PDS", "false").lower() == "true"

    if validation_strict_mode:
        logger.info("Lloyd George validation strict mode is enabled")

    if "Records" not in event or len(event["Records"]) < 1:
        http_status_code = 400
        response_body = (
            f"No sqs messages found in event: {event}. Will ignore this event"
        )
        logger.error(response_body, {"Result": "Bulk upload failed"})
        return ApiGatewayResponse(
            status_code=http_status_code, body=response_body, methods="GET"
        ).create_api_gateway_response()

    bulk_upload_service = BulkUploadService(
        strict_mode=validation_strict_mode, bypass_pds=bypass_pds
    )

    try:
        bulk_upload_service.process_message_queue(event["Records"])
        http_status_code = 200
        response_body = f"Finished processing all {len(event['Records'])} messages"
        logger.info(response_body)
    except BulkUploadException as e:
        http_status_code = 500
        response_body = f"Bulk upload failed with error: {e}"
        logger.error(str(e), {"Result": "Bulk upload failed"})

    return ApiGatewayResponse(
        status_code=http_status_code, body=response_body, methods="GET"
    ).create_api_gateway_response()
