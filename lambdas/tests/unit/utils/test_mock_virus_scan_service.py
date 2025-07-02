import pytest
from enums.virus_scan_result import VirusScanResult
from services.mock_virus_scan_service import MockVirusScanService


@pytest.fixture()
def mock_virus_scan_service():
    return MockVirusScanService()


def test_scan_file_clean(mock_virus_scan_service):
    result = mock_virus_scan_service.scan_file("test1")
    assert result == VirusScanResult.INFECTED


def test_scan_file_infected(mock_virus_scan_service):
    result = mock_virus_scan_service.scan_file("test2")
    assert result == VirusScanResult.CLEAN
