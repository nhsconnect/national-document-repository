import pytest
from handlers.bulk_upload_report_handler import lambda_handler
from botocore.exceptions import ClientError

from services.bulk_upload_report_service import BulkUploadReportService
from utils.exceptions import BulkUploadReportException


def test_bulk_upload_report_service_is_called(set_env, mocker, event, context):
    mock_report_handler = mocker.patch(
        "services.bulk_upload_report_service.BulkUploadReportService.report_handler"
    )

    lambda_handler(event, context)

    mock_report_handler.assert_called_once()


def test_client_error_is_thrown(mocker, event, context):
    exception = BulkUploadReportException("error")
    # mocker.patch("services.s3_service.S3Service.upload_file", side_effect=exception)
    mock_report_handler = mocker.patch(
        "services.bulk_upload_report_service.BulkUploadReportService.report_handler"
    )
    mock_report_handler.side_effect = exception

    with pytest.raises(BulkUploadReportException):
        lambda_handler(event, context)
