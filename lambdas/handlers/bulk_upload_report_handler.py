from enums.report_types import ReportType
from services.bulk_upload_report_service import BulkUploadReportService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.lambda_response import ApiGatewayResponse

logger = LoggingService(__name__)


@set_request_context_for_logging
@ensure_environment_variables(
    names=[
        "STAGING_STORE_BUCKET_NAME",
        "BULK_UPLOAD_DYNAMODB_NAME",
    ]
)
@override_error_check
@handle_lambda_exceptions
def lambda_handler(event, context):
    report_type = event.get("report_type", ReportType.CURRENT.value)
    logger.info(f"Starting {report_type} report process")

    bulk_upload_report_service = BulkUploadReportService()
    bulk_upload_report_service.report_handler(report_type)

    return ApiGatewayResponse(
        status_code=200,
        body=f"{report_type.capitalize()} report creation successful",
        methods="GET",
    ).create_api_gateway_response()
