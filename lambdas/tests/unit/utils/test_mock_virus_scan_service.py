import pytest
from enums.virus_scan_result import VirusScanResult
from services.mock_virus_scan_service import MockVirusScanService


@pytest.fixture()
def mock_virus_scan_service():
    return MockVirusScanService()


@pytest.fixture()
def mock_virus_scan_service_with_env_var(monkeypatch):
    monkeypatch.setenv("INFECTED_NHS_NUMBERS", "9000000004,9000000003")
    service = MockVirusScanService()
    monkeypatch.delenv("INFECTED_NHS_NUMBERS")
    return service


def test_scan_file_clean_without_nhs_number(mock_virus_scan_service):
    result = mock_virus_scan_service.scan_file("test1")
    assert result == VirusScanResult.CLEAN


def test_scan_file_infected(mock_virus_scan_service):
    result = mock_virus_scan_service.scan_file("test2", nhs_number="9000000114")
    assert result == VirusScanResult.INFECTED


def test_scan_file_clean_with_nhs_number(mock_virus_scan_service):
    result = mock_virus_scan_service.scan_file("test2", nhs_number="9000000004")
    assert result == VirusScanResult.CLEAN


def test_scan_file_infected_with_nhs_number_env_var(
    mock_virus_scan_service_with_env_var,
):
    result = mock_virus_scan_service_with_env_var.scan_file(
        "test2", nhs_number="9000000004"
    )
    assert result == VirusScanResult.INFECTED


def test_scan_file_clean_with_nhs_number_env_var(mock_virus_scan_service_with_env_var):
    result = mock_virus_scan_service_with_env_var.scan_file(
        "test2", nhs_number="9000000005"
    )
    assert result == VirusScanResult.CLEAN
