from enums.logging_app_interaction import LoggingAppInteraction
from services.lloyd_george_stitch_service import LloydGeorgeStitchService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.decorators.validate_patient_id import (
    extract_nhs_number_from_event,
    validate_patient_id,
)
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = LoggingService(__name__)


@set_request_context_for_logging
@validate_patient_id
@override_error_check
@handle_lambda_exceptions
@ensure_environment_variables(
    names=["LLOYD_GEORGE_DYNAMODB_NAME", "LLOYD_GEORGE_BUCKET_NAME"]
)
def lambda_handler(event, _context):
    request_context.app_interaction = LoggingAppInteraction.VIEW_LG_RECORD.value
    nhs_number = extract_nhs_number_from_event(event)
    request_context.patient_nhs_no = nhs_number

    stitch_service = LloydGeorgeStitchService()

    stitch_result = stitch_service.stitch_lloyd_george_record(nhs_number)
    return ApiGatewayResponse(200, stitch_result, "GET").create_api_gateway_response()
