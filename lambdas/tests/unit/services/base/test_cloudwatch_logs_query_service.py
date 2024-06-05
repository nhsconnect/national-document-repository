import pytest
from services.cloudwatch_logs_query_service import CloudwatchLogsQueryService


@pytest.fixture
def mock_service(set_env, mocker):
    mocker.patch("boto3.client")
    service = CloudwatchLogsQueryService()
    yield service


def test_singleton_instance(set_env):
    instance_1 = CloudwatchLogsQueryService()
    instance_2 = CloudwatchLogsQueryService()

    assert instance_1 is instance_2
