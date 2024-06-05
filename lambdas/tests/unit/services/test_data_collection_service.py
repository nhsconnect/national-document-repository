import pytest
from models.cloudwatch_logs_query import (
    CloudwatchLogsQueryParams,
    LloydGeorgeRecordsDeleted,
    LloydGeorgeRecordsDownloaded,
    LloydGeorgeRecordsStored,
    LloydGeorgeRecordsViewed,
    UniqueActiveUserIds,
)
from pytest_unordered import unordered
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
from tests.unit.data.statistic.expected_data import (
    MOCK_APPLICATION_DATA,
    MOCK_ORGANISATION_DATA,
    MOCK_RECORD_STORE_DATA,
)
from tests.unit.data.statistic.logs_query_results import (
    HASHED_USER_ID_1,
    HASHED_USER_ID_2,
    MOCK_LG_DELETED,
    MOCK_LG_DOWNLOADED,
    MOCK_LG_STORED,
    MOCK_LG_VIEWED,
    MOCK_UNIQUE_ACTIVE_USER_IDS,
)
from tests.unit.data.statistic.s3_list_objects_result import (
    MOCK_ARF_LIST_OBJECTS_RESULT,
    MOCK_LG_LIST_OBJECTS_RESULT,
    TOTAL_FILE_SIZE_FOR_H81109,
    TOTAL_FILE_SIZE_FOR_Y12345,
)


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
def mock_query_logs(mocker):
    def mock_implementation(query_params: CloudwatchLogsQueryParams, **_kwargs):
        if query_params == LloydGeorgeRecordsViewed:
            return MOCK_LG_VIEWED
        elif query_params == LloydGeorgeRecordsDownloaded:
            return MOCK_LG_DOWNLOADED
        elif query_params == LloydGeorgeRecordsDeleted:
            return MOCK_LG_DELETED
        elif query_params == LloydGeorgeRecordsStored:
            return MOCK_LG_STORED
        elif query_params == UniqueActiveUserIds:
            return MOCK_UNIQUE_ACTIVE_USER_IDS

    patched_instance = mocker.patch(
        "services.data_collection_service.CloudwatchLogsQueryService",
        spec=CloudwatchLogsQueryService,
    ).return_value
    mocked_method = patched_instance.query_logs
    mocked_method.side_effect = mock_implementation

    yield mocked_method


@pytest.fixture
def mock_service(set_env, mock_query_logs, mock_dynamodb_scan, mock_s3_list_objects):
    service = DataCollectionService()
    yield service


@pytest.fixture
def mock_uuid(mocker):
    yield mocker.patch("uuid.uuid4", return_value="mock_uuid")


def test_collect_all_data(mock_service, mock_uuid):
    actual = mock_service.collect_all_data()
    expected = unordered(
        MOCK_RECORD_STORE_DATA + MOCK_ORGANISATION_DATA + MOCK_APPLICATION_DATA
    )

    assert actual == expected


def test_get_record_store_data(mock_service, mock_uuid):
    mock_dynamo_scan_result = MOCK_ARF_SCAN_RESULT + MOCK_LG_SCAN_RESULT
    s3_list_objects_result = MOCK_ARF_LIST_OBJECTS_RESULT + MOCK_LG_LIST_OBJECTS_RESULT

    actual = mock_service.get_record_store_data(
        mock_dynamo_scan_result, s3_list_objects_result
    )
    expected = unordered(MOCK_RECORD_STORE_DATA)

    assert actual == expected


def test_get_organisation_data(mock_service, mock_uuid):
    mock_dynamo_scan_result = MOCK_ARF_SCAN_RESULT + MOCK_LG_SCAN_RESULT

    actual = mock_service.get_organisation_data(mock_dynamo_scan_result)
    expected = unordered(MOCK_ORGANISATION_DATA)

    assert actual == expected


def test_get_application_data(mock_service, mock_uuid):
    actual = mock_service.get_application_data()
    expected = unordered(MOCK_APPLICATION_DATA)

    assert actual == expected


def test_get_active_user_list(set_env, mock_query_logs):
    mock_query_logs.return_value = MOCK_UNIQUE_ACTIVE_USER_IDS
    service = DataCollectionService()
    expected = {
        "H81109": [
            HASHED_USER_ID_1,
            HASHED_USER_ID_2,
        ],
        "Y12345": [HASHED_USER_ID_1],
    }
    actual = service.get_active_user_list()

    assert actual == expected


def test_get_total_number_of_records(mock_service):
    actual = mock_service.get_total_number_of_records(MOCK_ARF_SCAN_RESULT)
    expected = [
        {"ods_code": "Y12345", "total_number_of_records": 2},
        {"ods_code": "H81109", "total_number_of_records": 1},
    ]

    assert actual == expected

    actual = mock_service.get_total_number_of_records(MOCK_LG_SCAN_RESULT)
    expected = [
        {"ods_code": "H81109", "total_number_of_records": 5},
    ]

    assert actual == expected

    actual = mock_service.get_total_number_of_records(
        MOCK_ARF_SCAN_RESULT + MOCK_LG_SCAN_RESULT
    )
    expected = [
        {"ods_code": "Y12345", "total_number_of_records": 2},
        {"ods_code": "H81109", "total_number_of_records": 6},
    ]

    assert actual == expected


def test_get_number_of_patients(mock_service):
    actual = mock_service.get_number_of_patients(MOCK_ARF_SCAN_RESULT)
    expected = [
        {"ods_code": "Y12345", "number_of_patients": 1},
        {"ods_code": "H81109", "number_of_patients": 1},
    ]

    assert actual == expected

    actual = mock_service.get_number_of_patients(
        MOCK_ARF_SCAN_RESULT + MOCK_LG_SCAN_RESULT
    )
    expected = [
        {"ods_code": "Y12345", "number_of_patients": 1},
        {"ods_code": "H81109", "number_of_patients": 2},
    ]

    assert actual == expected


def test_get_metrics_for_total_and_average_file_sizes(mock_service):
    mock_dynamo_scan_result = MOCK_ARF_SCAN_RESULT + MOCK_LG_SCAN_RESULT
    s3_list_objects_result = MOCK_ARF_LIST_OBJECTS_RESULT + MOCK_LG_LIST_OBJECTS_RESULT

    actual = mock_service.get_metrics_for_total_and_average_file_sizes(
        mock_dynamo_scan_result, s3_list_objects_result
    )

    expected = [
        {
            "ods_code": "H81109",
            "average_size_of_documents_per_patient_in_megabytes": TOTAL_FILE_SIZE_FOR_H81109
            / 2,
            "total_size_of_records_in_megabytes": TOTAL_FILE_SIZE_FOR_H81109,
        },
        {
            "ods_code": "Y12345",
            "average_size_of_documents_per_patient_in_megabytes": TOTAL_FILE_SIZE_FOR_Y12345,
            "total_size_of_records_in_megabytes": TOTAL_FILE_SIZE_FOR_Y12345,
        },
    ]

    assert actual == expected


def test_get_number_of_document_types(mock_service):
    actual = mock_service.get_number_of_document_types(MOCK_ARF_SCAN_RESULT)
    expected = [
        {"ods_code": "Y12345", "number_of_document_types": 2},
        {"ods_code": "H81109", "number_of_document_types": 1},
    ]

    assert actual == expected

    actual = mock_service.get_number_of_document_types(
        MOCK_ARF_SCAN_RESULT + MOCK_LG_SCAN_RESULT
    )
    expected = [
        {"ods_code": "Y12345", "number_of_document_types": 2},
        {"ods_code": "H81109", "number_of_document_types": 2},
    ]

    assert actual == expected
