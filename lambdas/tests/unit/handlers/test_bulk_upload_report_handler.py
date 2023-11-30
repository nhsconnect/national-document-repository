from botocore.exceptions import ClientError
from handlers.bulk_upload_report_handler import lambda_handler


def test_bulk_upload_report_lambda_handler_valid(set_env, mocker, event, context):
    mock_report_handler = mocker.patch(
        "services.bulk_upload_report_service.BulkUploadReportService.report_handler"
    )

    response = lambda_handler(event, context)

    mock_report_handler.assert_called_once()

    assert response["statusCode"] == 200
    assert response["body"] == "Bulk upload report creation successful"


def test_bulk_upload_report_lambda_handler_client_error(
    set_env, mocker, event, context
):
    mock_report_handler = mocker.patch(
        "services.bulk_upload_report_service.BulkUploadReportService.report_handler",
        side_effect=ClientError({"error": "test error message"}, "test"),
    )

    response = lambda_handler(event, context)

    mock_report_handler.assert_called_once()

    assert response["statusCode"] == 500
    assert (
        response["body"]
        == "Bulk upload report creation failed: An error occurred (Unknown) when calling the test operation: Unknown"
    )
