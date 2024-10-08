import json

from botocore.exceptions import ClientError
from handlers.bulk_upload_report_handler import lambda_handler


def test_bulk_upload_report_lambda_handler_valid(set_env, mocker, event, context):
    mock_report_handler = mocker.patch(
        "services.bulk_upload_report_service.BulkUploadReportService.report_handler"
    )

    response = lambda_handler(event, context)

    assert response["statusCode"] == 200
    assert (
        response["body"] == "Bulk upload summary and ODS reports created successfully"
    )

    mock_report_handler.assert_called_once()


def test_bulk_upload_report_lambda_handler_client_error(
    set_env, mocker, event, context
):
    mock_report_handler = mocker.patch(
        "services.bulk_upload_report_service.BulkUploadReportService.report_handler",
        side_effect=ClientError({"error": "test error message"}, "test"),
    )

    response = lambda_handler(event, context)
    response_body = json.loads(response["body"])
    assert response["statusCode"] == 500
    assert response_body["message"] == "Failed to utilise AWS client/resource"
    assert response_body["err_code"] == "GWY_5001"
    mock_report_handler.assert_called_once()
