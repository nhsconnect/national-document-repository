from services.ods_report_service import OdsReportService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check

logger = LoggingService(__name__)


@ensure_environment_variables(
    names=[
        "LLOYD_GEORGE_DYNAMODB_NAME",
    ]
)
@override_error_check
@handle_lambda_exceptions
def lambda_handler(event, context):
    ods_codes = event["queryStringParameters"]["odsCode"]

    service = OdsReportService()
    ods_code_list = ods_codes.split(",")
    for code in ods_code_list:
        logger.info("Starting process for ods code: %s", code)
        service.get_nhs_numbers_by_ods(code)
