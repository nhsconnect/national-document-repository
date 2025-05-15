import json

from enums.file_type import FileType
from enums.logging_app_interaction import LoggingAppInteraction
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
        "PRESIGNED_ASSUME_ROLE",
        "LLOYD_GEORGE_DYNAMODB_NAME",
        "STATISTICAL_REPORTS_BUCKET",
    ]
)
@override_error_check
@handle_lambda_exceptions
@set_request_context_for_logging
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.ODS_REPORT.value

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

    params = event.get("queryStringParameters") or {}
    file_type = params.get("outputFileFormat", "")
    if file_type not in FileType.__members__.values():
        file_type = FileType.CSV

    service = OdsReportService()
    logger.info(f"Received a request to create a report for ODS code: {ods_code}")
    pre_signed_url = service.create_and_save_ods_report_based_on_ods(
        ods_code=ods_code,
        is_pre_signed_needed=True,
        is_upload_to_s3_needed=True,
        file_type_output=file_type,
    )
    logger.info("A report has been successfully created.")
    return ApiGatewayResponse(
        200, json.dumps({"url": pre_signed_url}), "GET"
    ).create_api_gateway_response()


def handle_manual_trigger(event):
    ods_codes = event.get("odsCode").split(",")
    file_type = event.get("outputFileFormat")
    if file_type not in FileType.__members__.values():
        file_type = FileType.CSV

    service = OdsReportService()
    for ods_code in ods_codes:
        logger.info(f"Starting process for ods code: {ods_code}")
        service.create_and_save_ods_report_based_on_ods(
            ods_code=ods_code, is_upload_to_s3_needed=True, file_type_output=file_type
        )
    return ApiGatewayResponse(
        200, "Successfully created report", "GET"
    ).create_api_gateway_response()
