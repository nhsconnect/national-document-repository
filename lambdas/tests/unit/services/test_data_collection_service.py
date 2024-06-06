from datetime import datetime
from decimal import Decimal
from random import shuffle
from unittest.mock import call

import pytest
from freezegun import freeze_time
from models.cloudwatch_logs_query import (
    CloudwatchLogsQueryParams,
    LloydGeorgeRecordsDeleted,
    LloydGeorgeRecordsDownloaded,
    LloydGeorgeRecordsStored,
    LloydGeorgeRecordsViewed,
    UniqueActiveUserIds,
)
from pytest_unordered import unordered
from services.base.cloudwatch_logs_query_service import CloudwatchLogsQueryService
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from services.data_collection_service import DataCollectionService
from tests.unit.conftest import (
    MOCK_ARF_BUCKET,
    MOCK_ARF_TABLE_NAME,
    MOCK_LG_BUCKET,
    MOCK_LG_TABLE_NAME,
    MOCK_STATISTICS_TABLE,
)
from tests.unit.data.statistic.expected_data import (
    ALL_MOCK_DATA_AS_JSON_LIST,
    MOCK_APPLICATION_DATA,
    MOCK_ORGANISATION_DATA,
    MOCK_RECORD_STORE_DATA,
)
from tests.unit.data.statistic.mock_dynamodb_and_s3_records import (
    MOCK_ARF_LIST_OBJECTS_RESULT,
    MOCK_ARF_SCAN_RESULT,
    MOCK_LG_LIST_OBJECTS_RESULT,
    MOCK_LG_SCAN_RESULT,
    TOTAL_FILE_SIZE_FOR_H81109,
    TOTAL_FILE_SIZE_FOR_Y12345,
    build_mock_results,
)
from tests.unit.data.statistic.mock_logs_query_results import (
    HASHED_USER_ID_1,
    HASHED_USER_ID_2,
    MOCK_LG_DELETED,
    MOCK_LG_DOWNLOADED,
    MOCK_LG_STORED,
    MOCK_LG_VIEWED,
    MOCK_UNIQUE_ACTIVE_USER_IDS,
)
from utils.common_query_filters import UploadCompleted


@pytest.fixture
def mock_dynamo_service(mocker):
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

    yield patched_instance


@pytest.fixture
def mock_s3_list_all_objects(mocker):
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
def mock_service(
    set_env, mock_query_logs, mock_dynamo_service, mock_s3_list_all_objects
):
    service = DataCollectionService()
    yield service


@pytest.fixture
def mock_uuid(mocker):
    yield mocker.patch("uuid.uuid4", return_value="mock_uuid")


@pytest.fixture
def larger_mock_data():
    dynamodb_1, s3_1 = build_mock_results("H81109", "9000000001", 135, 123)
    dynamodb_2, s3_2 = build_mock_results("H81109", "9000000002", 246, 456)
    dynamodb_3, s3_3 = build_mock_results("H81109", "9000000003", 369, 789)
    dynamodb_4, s3_4 = build_mock_results("Y12345", "9000000004", 4812, 9876)
    dynamodb_5, s3_5 = build_mock_results("Y12345", "9000000005", 5101, 5432)

    mock_dynamo_scan_result = (
        dynamodb_1 + dynamodb_2 + dynamodb_3 + dynamodb_4 + dynamodb_5
    )
    mock_s3_list_objects_result = s3_1 + s3_2 + s3_3 + s3_4 + s3_5
    shuffle(mock_dynamo_scan_result)
    shuffle(mock_s3_list_objects_result)

    return mock_dynamo_scan_result, mock_s3_list_objects_result


def test_collect_all_data_and_write_to_dynamodb(mock_service, mocker):
    mock_collected_data = ["testing1234"]
    mock_service.collect_all_data = mocker.MagicMock(return_value=mock_collected_data)
    mock_service.write_to_local_dynamodb_table = mocker.MagicMock()

    mock_service.collect_all_data_and_write_to_dynamodb()

    mock_service.collect_all_data.assert_called_once()
    mock_service.write_to_local_dynamodb_table.assert_called_with(mock_collected_data)


def test_collect_all_data(mock_service, mock_uuid):
    actual = mock_service.collect_all_data()
    expected = unordered(
        MOCK_RECORD_STORE_DATA + MOCK_ORGANISATION_DATA + MOCK_APPLICATION_DATA
    )

    assert actual == expected


def test_write_to_local_dynamodb_table(mock_dynamo_service, mock_service):
    mock_data = MOCK_RECORD_STORE_DATA + MOCK_ORGANISATION_DATA + MOCK_APPLICATION_DATA
    mock_service.write_to_local_dynamodb_table(mock_data)

    mock_dynamo_service.batch_writing.assert_called_with(
        table_name=MOCK_STATISTICS_TABLE, item_list=ALL_MOCK_DATA_AS_JSON_LIST
    )


def test_scan_dynamodb_tables(mock_dynamo_service, mock_service):
    mock_service.scan_dynamodb_tables()

    expected_project_expression = "CurrentGpOds,NhsNumber,FileLocation,ContentType"
    expected_filter_expression = UploadCompleted

    expected_calls = [
        call(
            table_name=MOCK_ARF_TABLE_NAME,
            project_expression=expected_project_expression,
            filter_expression=expected_filter_expression,
        ),
        call(
            table_name=MOCK_LG_TABLE_NAME,
            project_expression=expected_project_expression,
            filter_expression=expected_filter_expression,
        ),
    ]
    mock_dynamo_service.scan_whole_table.assert_has_calls(expected_calls)


def test_get_all_s3_files_info(mock_s3_list_all_objects, mock_service):
    mock_service.get_all_s3_files_info()

    expected_calls = [
        call(MOCK_ARF_BUCKET),
        call(MOCK_LG_BUCKET),
    ]

    mock_s3_list_all_objects.assert_has_calls(expected_calls)


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


@freeze_time("2024-06-04T10:25:00")
def test_get_cloud_watch_query_result(set_env, mock_query_logs):
    mock_query_param = CloudwatchLogsQueryParams("mock", "test")
    service = DataCollectionService()
    expected_start_time = datetime.fromisoformat("2024-06-03T10:25:00").timestamp()
    expected_end_time = datetime.fromisoformat("2024-06-04T10:25:00").timestamp()

    service.get_cloud_watch_query_result(mock_query_param)

    mock_query_logs.assert_called_with(
        query_params=mock_query_param,
        start_time=expected_start_time,
        end_time=expected_end_time,
    )


def test_get_total_number_of_records(mock_service):
    actual = mock_service.get_total_number_of_records(
        MOCK_ARF_SCAN_RESULT + MOCK_LG_SCAN_RESULT
    )
    expected = [
        {"ods_code": "Y12345", "total_number_of_records": 2},
        {"ods_code": "H81109", "total_number_of_records": 6},
    ]

    assert actual == expected


def test_get_total_number_of_records_larger_mock_data(mock_service, larger_mock_data):
    mock_dynamo_scan_result, _ = larger_mock_data

    actual = mock_service.get_total_number_of_records(mock_dynamo_scan_result)
    expected = unordered(
        [
            {"ods_code": "H81109", "total_number_of_records": 135 + 246 + 369},
            {"ods_code": "Y12345", "total_number_of_records": 4812 + 5101},
        ]
    )

    assert actual == expected


def test_get_number_of_patients(mock_service):
    actual = mock_service.get_number_of_patients(
        MOCK_ARF_SCAN_RESULT + MOCK_LG_SCAN_RESULT
    )
    expected = unordered(
        [
            {"ods_code": "Y12345", "number_of_patients": 1},
            {"ods_code": "H81109", "number_of_patients": 2},
        ]
    )

    assert actual == expected


def test_get_metrics_for_total_and_average_file_sizes(mock_service):
    mock_dynamo_scan_result = MOCK_ARF_SCAN_RESULT + MOCK_LG_SCAN_RESULT
    mock_s3_list_objects_result = (
        MOCK_ARF_LIST_OBJECTS_RESULT + MOCK_LG_LIST_OBJECTS_RESULT
    )

    actual = mock_service.get_metrics_for_total_and_average_file_sizes(
        mock_dynamo_scan_result, mock_s3_list_objects_result
    )

    expected = unordered(
        [
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
    )

    assert actual == expected


def test_get_metrics_for_total_and_average_file_sizes_larger_mock_data(
    mock_service, larger_mock_data
):
    mock_dynamo_scan_result, mock_s3_list_objects_result = larger_mock_data
    actual = mock_service.get_metrics_for_total_and_average_file_sizes(
        mock_dynamo_scan_result, mock_s3_list_objects_result
    )

    expected = unordered(
        [
            {
                "ods_code": "H81109",
                "average_size_of_documents_per_patient_in_megabytes": (123 + 456 + 789)
                / 3,
                "total_size_of_records_in_megabytes": (123 + 456 + 789),
            },
            {
                "ods_code": "Y12345",
                "average_size_of_documents_per_patient_in_megabytes": (9876 + 5432) / 2,
                "total_size_of_records_in_megabytes": (9876 + 5432),
            },
        ]
    )

    assert actual == expected


def test_get_number_of_document_types(mock_service):
    actual = mock_service.get_number_of_document_types(MOCK_ARF_SCAN_RESULT)
    expected = unordered(
        [
            {"ods_code": "Y12345", "number_of_document_types": 2},
            {"ods_code": "H81109", "number_of_document_types": 1},
        ]
    )

    assert actual == expected

    actual = mock_service.get_number_of_document_types(
        MOCK_ARF_SCAN_RESULT + MOCK_LG_SCAN_RESULT
    )
    expected = unordered(
        [
            {"ods_code": "Y12345", "number_of_document_types": 2},
            {"ods_code": "H81109", "number_of_document_types": 2},
        ]
    )

    assert actual == expected


def test_get_average_number_of_file_per_patient(mock_service):
    actual = mock_service.get_average_number_of_file_per_patient(
        MOCK_ARF_SCAN_RESULT + MOCK_LG_SCAN_RESULT
    )
    expected = unordered(
        [
            {"ods_code": "Y12345", "average_records_per_patient": 2},
            {"ods_code": "H81109", "average_records_per_patient": 3},
        ]
    )

    assert actual == expected


def test_get_average_number_of_file_per_patient_larger_mock_data(
    mock_service, larger_mock_data
):
    mock_dynamo_scan_result, _ = larger_mock_data

    actual = mock_service.get_average_number_of_file_per_patient(
        mock_dynamo_scan_result
    )
    expected = unordered(
        [
            {
                "ods_code": "H81109",
                "average_records_per_patient": Decimal(135 + 246 + 369) / 3,
            },
            {
                "ods_code": "Y12345",
                "average_records_per_patient": Decimal(4812 + 5101) / 2,
            },
        ]
    )

    assert actual == expected
