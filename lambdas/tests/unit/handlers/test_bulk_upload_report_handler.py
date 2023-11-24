import pytest
from services.bulk_upload_report_service import BulkUploadReportService


@pytest.fixture(scope="function")
def mock_bulk_upload_report_service():
    mock_bulk_upload_report_service = BulkUploadReportService()
    yield mock_bulk_upload_report_service
