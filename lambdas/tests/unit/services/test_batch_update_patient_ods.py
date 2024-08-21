import pytest
from requests import Response
from services.batch_update_ods_code import BatchUpdate

from ..conftest import MOCK_LG_TABLE_NAME_ENV_NAME


@pytest.fixture
def mock_update_ods_service(mocker, set_env):
    service = BatchUpdate(MOCK_LG_TABLE_NAME_ENV_NAME)
    mocker.patch.object(service, "pds_service")
    yield service


@pytest.fixture
def mock_pds_service(mocker, mock_update_ods_service):
    mock_pds_service = mock_update_ods_service.pds_service
    mocker.patch.object(mock_pds_service, "pds_request")
    yield mock_pds_service


@pytest.fixture
def mock_valid_pds_response_patient_deceased():
    mock_response = Response()
    mock_response.status_code = 200
    with open(
        "services/mock_data/pds_patient_9000000202_M85143_deceased_formal.json", "rb"
    ) as f:
        mock_data = f.read()
    mock_response._content = mock_data
    yield mock_response


@pytest.fixture
def mock_valid_pds_response_patient_suspended():
    mock_response = Response()
    mock_response.status_code = 200
    with open("services/mock_data/pds_patient_9000000005_not_active.json", "rb") as f:
        mock_data = f.read()
    mock_response._content = mock_data
    yield mock_response


def test_get_updated_gp_ods_returns_DECE_if_patient_is_deceased(
    mock_update_ods_service, mock_pds_service, mock_valid_pds_response_patient_deceased
):
    mock_pds_service.pds_request.return_value = mock_valid_pds_response_patient_deceased

    assert mock_update_ods_service.get_updated_gp_ods("9000000202") == "DECE"


def test_get_updated_gp_ods_returns_SUSP_if_patient_is_inactive(
    mock_update_ods_service, mock_pds_service, mock_valid_pds_response_patient_suspended
):
    mock_pds_service.pds_request.return_value = (
        mock_valid_pds_response_patient_suspended
    )

    assert mock_update_ods_service.get_updated_gp_ods("9000000005") == "SUSP"


def test_get_updated_gp_ods_returns_patient_ods_code(
    mock_update_ods_service, mock_pds_service, mock_valid_pds_response
):
    mock_pds_service.pds_request.return_value = mock_valid_pds_response

    assert mock_update_ods_service.get_updated_gp_ods("9000000002") == "H81109"
