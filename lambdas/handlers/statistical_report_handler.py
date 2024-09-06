from services.statistical_report_service import StatisticalReportService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables_for_non_webapi
from utils.decorators.override_error_check import override_error_check
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions

logger = LoggingService(__name__)


@ensure_environment_variables_for_non_webapi(
    names=[
        "WORKSPACE",
        "STATISTICS_TABLE",
        "STATISTICAL_REPORTS_BUCKET",
    ]
)
@override_error_check
@handle_lambda_exceptions
def lambda_handler(_event, _context):
    logger.info("Starting creating statistical report")
    service = StatisticalReportService()
    service.make_weekly_summary_and_output_to_bucket()
