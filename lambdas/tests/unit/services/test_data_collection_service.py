import pytest
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from services.data_collection_service import DataCollectionService
from services.logs_query_service import CloudwatchLogsQueryService
from tests.unit.conftest import (
    MOCK_ARF_BUCKET,
    MOCK_ARF_TABLE_NAME,
    MOCK_LG_BUCKET,
    MOCK_LG_TABLE_NAME,
)
from tests.unit.data.statistic.dynamodb_scan_result import (
    MOCK_ARF_SCAN_RESULT,
    MOCK_LG_SCAN_RESULT,
)
from tests.unit.data.statistic.logs_query_results import UNIQUE_ACTIVE_USER_IDS
from tests.unit.data.statistic.s3_list_objects_result import (
    MOCK_ARF_LIST_OBJECTS_RESULT,
    MOCK_LG_LIST_OBJECTS_RESULT,
)


@pytest.fixture
def mock_logs_query_service(mocker):
    patched_instance = mocker.patch(
        "services.data_collection_service.CloudwatchLogsQueryService",
        spec=CloudwatchLogsQueryService,
    ).return_value
    yield patched_instance


@pytest.fixture
def mock_dynamodb_scan(mocker):
    def mock_implementation(table_name, **_kwargs):
        if table_name == MOCK_LG_TABLE_NAME:
            return MOCK_LG_SCAN_RESULT
        elif table_name == MOCK_ARF_TABLE_NAME:
            return MOCK_ARF_SCAN_RESULT

    patched_instance = mocker.patch(
        "services.data_collection_service.DynamoDBService", spec=DynamoDBService
    ).return_value
    patched_method = patched_instance.scan_whole_table
    patched_method.side_effect = mock_implementation

    yield patched_method


@pytest.fixture
def mock_s3_list_objects(mocker):
    def mock_implementation(bucket_name, **_kwargs):
        if bucket_name == MOCK_LG_BUCKET:
            return MOCK_LG_LIST_OBJECTS_RESULT
        elif bucket_name == MOCK_ARF_BUCKET:
            return MOCK_ARF_LIST_OBJECTS_RESULT

    patched_instance = mocker.patch(
        "services.data_collection_service.S3Service", spec=S3Service
    ).return_value
    patched_method = patched_instance.list_all_objects
    patched_method.side_effect = mock_implementation

    yield patched_method


@pytest.fixture
def mock_service(mock_logs_query_service, mock_dynamodb_scan, mock_s3_list_objects):
    service = DataCollectionService()
    yield service


def test_collect_all_data(set_env, mock_service):
    actual = mock_service.collect_all_data()
    expected = {}

    assert actual == expected


def test_get_active_user_list(set_env, mock_logs_query_service):
    mock_logs_query_service.query_logs.return_value = UNIQUE_ACTIVE_USER_IDS
    service = DataCollectionService()
    expected = {
        "H81109": [
            "e807f1fcf82d132f9bb018ca6738a19f",
            "b1fa0218c1040b082e2374a941707c35",
        ],
        "Y12345": ["e807f1fcf82d132f9bb018ca6738a19f"],
    }
    actual = service.get_active_user_list()

    assert actual == expected
