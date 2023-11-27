from handlers.bulk_upload_report_handler import lambda_handler


def test_bulk_upload_report_service_is_called(set_env, mocker, event, context):
    mock_report_handler = mocker.patch(
        "services.bulk_upload_report_service.BulkUploadReportService.report_handler"
    )

    lambda_handler(event, context)

    mock_report_handler.assert_called_once()


def test_client_error_is_thrown(mocker, event, context):
    pass
