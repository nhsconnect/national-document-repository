import pytest
from scripts.batch_update_ods_code import BatchUpdate


@pytest.fixture
def mock_update_ods_service(mocker, set_env):
    service = BatchUpdate()
    mocker.patch.object(service, "dynamo_service")
    yield service
