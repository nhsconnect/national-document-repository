from services.bulk_upload_report_service import BulkUploadReportService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.exceptions import BulkUploadReportException

logger = LoggingService(__name__)
bulk_upload_report_service = BulkUploadReportService()


@set_request_context_for_logging
@ensure_environment_variables(
    names=[
        "STAGING_STORE_BUCKET_NAME",
        "BULK_UPLOAD_DYNAMODB_NAME",
    ]
)
@override_error_check
def lambda_handler(event, context):
    try:
        bulk_upload_report_service.report_handler()
    except BulkUploadReportException as e:
        logger.error(str(e))
