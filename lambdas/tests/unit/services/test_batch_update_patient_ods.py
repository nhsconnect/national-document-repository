import pytest
from services.batch_update_ods_code import BatchUpdate


@pytest.fixture
def mock_update_ods_service(mocker, set_env):
    service = BatchUpdate()
    mocker.patch.object(service, "dynamo_service")
    yield service


def test_get_updated_gp_ods_returns_DECE_if_patient_is_deceased():
    pass


def test_get_updated_gp_ods_returns_SUSP_if_patient_is_inactive():
    pass


def test_get_updated_gp_ods_returns_patient_ods_code():
    pass
