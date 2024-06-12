import pytest
from handlers.statistical_report_handler import lambda_handler
from services.statistical_report_service import StatisticalReportService
from utils.exceptions import MissingEnvVarException


def test_lambda_handler_call_underlying_service(mocker, context, set_env):
    mock_statistical_report_service = mocker.patch(
        "handlers.statistical_report_handler.StatisticalReportService",
        spec=StatisticalReportService,
    ).return_value

    lambda_handler(None, context)

    mock_statistical_report_service.make_weekly_summary_and_output_to_bucket.assert_called_once()


def test_lambda_handler_check_for_env_vars(context):
    with pytest.raises(MissingEnvVarException) as error:
        lambda_handler(None, context)

    assert "An error occurred due to missing environment variable" in str(error.value)
