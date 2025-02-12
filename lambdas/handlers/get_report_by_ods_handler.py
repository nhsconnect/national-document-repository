import json

from services.ods_report_service import OdsReportService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.exceptions import OdsErrorException
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = LoggingService(__name__)


@ensure_environment_variables(
    names=[
        "LLOYD_GEORGE_DYNAMODB_NAME",
    ]
)
@override_error_check
@handle_lambda_exceptions
@set_request_context_for_logging
def lambda_handler(event, context):
    if "httpMethod" in event:
        return handle_api_gateway_request(event)
    else:
        return handle_manual_trigger(event)


def handle_api_gateway_request(event):
    ods_code = request_context.authorization.get("selected_organisation", {}).get(
        "org_ods_code"
    )
    if not ods_code:
        raise OdsErrorException("No ODS code provided")
    service = OdsReportService()
    logger.info(f"Starting process for ods code: {ods_code}")
    pre_sign_url = service.get_nhs_numbers_by_ods(ods_code, is_pre_signed_need=True)
    return ApiGatewayResponse(
        200, json.dumps({"url": pre_sign_url}), "GET"
    ).create_api_gateway_response()


def handle_manual_trigger(event):
    ods_codes = event.get("odsCode").split(",")

    service = OdsReportService()
    for ods_code in ods_codes:
        logger.info(f"Starting process for ods code: {ods_code}")
        service.get_nhs_numbers_by_ods(ods_code)
