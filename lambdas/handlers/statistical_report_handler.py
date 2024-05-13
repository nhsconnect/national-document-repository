from services.statistical_report_service import StatisticalReportService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check

logger = LoggingService(__name__)


@ensure_environment_variables(
    names=[
        "WORKSPACE",
        "STATISTICS_TABLE",
        "STATISTICAL_REPORTS_BUCKET",
    ]
)
@override_error_check
@handle_lambda_exceptions
def lambda_handler(event, context):
    logger.info("Starting creating statistical report")
    service = StatisticalReportService()
    service.make_weekly_summary()
