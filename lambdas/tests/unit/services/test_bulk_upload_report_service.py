import os
from datetime import datetime
from unittest.mock import call

import pytest
from boto3.dynamodb.conditions import Attr
from freezegun import freeze_time
from services.bulk_upload_report_service import BulkUploadReportService, OdsReport
from tests.unit.conftest import (
    MOCK_BULK_REPORT_TABLE_NAME,
    MOCK_STATISTICS_REPORT_BUCKET_NAME,
    TEST_CURRENT_GP_ODS,
    TEST_UUID,
)
from tests.unit.helpers.data.bulk_upload.test_data import readfile
from tests.unit.helpers.data.dynamo_scan_response import (
    EXPECTED_RESPONSE,
    MOCK_EMPTY_RESPONSE,
    MOCK_RESPONSE,
    MOCK_RESPONSE_WITH_LAST_KEY,
    UNEXPECTED_RESPONSE,
)
from tests.unit.models.test_bulk_upload_status import (
    MOCK_DATA_COMPLETE_UPLOAD,
    MOCK_DATA_FAILED_UPLOAD,
)

MOCK_END_REPORT_TIME = datetime(2012, 1, 14, 7, 0, 0, 0)
MOCK_START_REPORT_TIME = datetime(2012, 1, 13, 7, 0, 0, 0)
MOCK_BULK_REPORT_TABLE_RESPONSE = [
    {
        "Timestamp": 1688395680,
        "Date": "2012-01-13",
        "NhsNumber": "9000000011",
        "FilePath": "/9000000011/1of1_Lloyd_George_Record_[NAME]_[9000000011]_[DOB].pdf",
        "UploaderOdsCode": "TEST",
        "UploadStatus": "complete",
        "ID": TEST_UUID,
        "PdsOdsCode": "TEST",
    },
    {
        "Timestamp": 1688395680,
        "Date": "2012-01-13",
        "NhsNumber": "9000000011",
        "FilePath": "/9000000011/1of1_Lloyd_George_Record_[NAME]_[9000000011]_[DOB].pdf",
        "UploaderOdsCode": "TEST",
        "UploadStatus": "complete",
        "ID": TEST_UUID,
        "PdsOdsCode": "TEST",
    },
    {
        "Timestamp": 1688395681,
        "Date": "2012-01-13",
        "NhsNumber": "9000000010",
        "FilePath": "/9000000010/1of2_Lloyd_George_Record_[NAME_2]_[9000000010]_[DOB].pdf",
        "UploaderOdsCode": "TEST",
        "FailureReason": "Could not find the given patient on PDS",
        "UploadStatus": "failed",
        "ID": TEST_UUID,
        "PdsOdsCode": "",
    },
    {
        "Timestamp": 1688395681,
        "Date": "2012-01-13",
        "NhsNumber": "9000000010",
        "FilePath": "/9000000010/2of2_Lloyd_George_Record_[NAME_2]_[9000000010]_[DOB].pdf",
        "UploaderOdsCode": "TEST",
        "FailureReason": "Could not find the given patient on PDS",
        "UploadStatus": "failed",
        "ID": TEST_UUID,
        "PdsOdsCode": "",
    },
]


@pytest.fixture
def bulk_upload_report_service(set_env, mocker):
    patched_bulk_upload_report_service = BulkUploadReportService()
    mocker.patch.object(patched_bulk_upload_report_service, "db_service")
    mocker.patch.object(patched_bulk_upload_report_service, "s3_service")

    yield patched_bulk_upload_report_service


@pytest.fixture
def mock_get_db_report_items(bulk_upload_report_service, mocker):
    yield mocker.patch.object(bulk_upload_report_service, "get_dynamodb_report_items")


@pytest.fixture
def mock_write_summary_data_to_csv(bulk_upload_report_service, mocker):
    yield mocker.patch.object(bulk_upload_report_service, "write_summary_data_to_csv")


@pytest.fixture
def mock_write_items_to_csv(bulk_upload_report_service, mocker):
    yield mocker.patch.object(bulk_upload_report_service, "write_items_to_csv")


@pytest.fixture
def mock_get_db_with_data(mocker, bulk_upload_report_service):
    yield mocker.patch.object(
        bulk_upload_report_service,
        "get_dynamodb_report_items",
        return_value=[MOCK_DATA_COMPLETE_UPLOAD],
    )


@pytest.fixture
def mock_get_times_for_scan(bulk_upload_report_service, mocker):
    yield mocker.patch.object(
        bulk_upload_report_service,
        "get_times_for_scan",
        return_value=(MOCK_START_REPORT_TIME, MOCK_END_REPORT_TIME),
    )


@freeze_time("2012-01-14 7:20:01")
def test_get_time_for_scan_after_7am(bulk_upload_report_service):

    (
        actual_start_time,
        actual_end_time,
    ) = bulk_upload_report_service.get_times_for_scan()

    assert MOCK_START_REPORT_TIME == actual_start_time
    assert MOCK_END_REPORT_TIME == actual_end_time


@freeze_time("2012-01-14 6:59:59")
def test_get_time_for_scan_before_7am(bulk_upload_report_service):
    expected_end_report_time = datetime(2012, 1, 13, 7, 0, 0, 0)
    expected_start_report_time = datetime(2012, 1, 12, 7, 0, 0, 0)

    (
        actual_start_time,
        actual_end_time,
    ) = bulk_upload_report_service.get_times_for_scan()

    assert expected_start_report_time == actual_start_time
    assert expected_end_report_time == actual_end_time


@freeze_time("2012-01-14 7:00:00")
def test_get_time_for_scan_at_7am(bulk_upload_report_service):
    expected_end_report_time = datetime(2012, 1, 14, 7, 0, 0, 0)
    expected_start_report_time = datetime(2012, 1, 13, 7, 0, 0, 0)

    (
        actual_start_time,
        actual_end_time,
    ) = bulk_upload_report_service.get_times_for_scan()

    assert expected_start_report_time == actual_start_time
    assert expected_end_report_time == actual_end_time


def test_get_dynamo_data_2_calls(bulk_upload_report_service):
    mock_filter = Attr("Timestamp").gt(MOCK_START_REPORT_TIME) & Attr("Timestamp").lt(
        MOCK_END_REPORT_TIME
    )
    mock_last_key = {"FileName": "Screenshot 2023-08-15 at 16.17.56.png"}
    bulk_upload_report_service.db_service.scan_table.side_effect = [
        MOCK_RESPONSE_WITH_LAST_KEY,
        MOCK_RESPONSE,
    ]

    actual = bulk_upload_report_service.get_dynamodb_report_items(
        MOCK_START_REPORT_TIME, MOCK_END_REPORT_TIME
    )

    assert actual == EXPECTED_RESPONSE * 2
    assert bulk_upload_report_service.db_service.scan_table.call_count == 2
    calls = [
        call(MOCK_BULK_REPORT_TABLE_NAME, filter_expression=mock_filter),
        call(
            MOCK_BULK_REPORT_TABLE_NAME,
            exclusive_start_key=mock_last_key,
            filter_expression=mock_filter,
        ),
    ]
    bulk_upload_report_service.db_service.scan_table.assert_has_calls(calls)


def test_get_dynamo_data_with_no_start_key(bulk_upload_report_service):
    mock_filter = Attr("Timestamp").gt(MOCK_START_REPORT_TIME) & Attr("Timestamp").lt(
        MOCK_END_REPORT_TIME
    )
    bulk_upload_report_service.db_service.scan_table.side_effect = [MOCK_RESPONSE]

    actual = bulk_upload_report_service.get_dynamodb_report_items(
        MOCK_START_REPORT_TIME, MOCK_END_REPORT_TIME
    )

    assert actual == EXPECTED_RESPONSE
    bulk_upload_report_service.db_service.scan_table.assert_called_once()
    bulk_upload_report_service.db_service.scan_table.assert_called_with(
        MOCK_BULK_REPORT_TABLE_NAME, filter_expression=mock_filter
    )


def test_get_dynamo_data_with_no_items(bulk_upload_report_service):
    bulk_upload_report_service.db_service.scan_table.side_effect = [MOCK_EMPTY_RESPONSE]

    actual = bulk_upload_report_service.get_dynamodb_report_items(
        MOCK_START_REPORT_TIME, MOCK_END_REPORT_TIME
    )

    assert actual == []
    bulk_upload_report_service.db_service.scan_table.assert_called_once()


def test_get_dynamo_data_with_bad_response(bulk_upload_report_service):
    bulk_upload_report_service.db_service.scan_table.side_effect = [UNEXPECTED_RESPONSE]

    actual = bulk_upload_report_service.get_dynamodb_report_items(
        MOCK_START_REPORT_TIME, MOCK_END_REPORT_TIME
    )

    assert actual is None
    bulk_upload_report_service.db_service.scan_table.assert_called_once()


def test_report_handler_no_items_returns_expected_log(
    bulk_upload_report_service,
    caplog,
    mock_get_db_report_items,
    mock_write_items_to_csv,
    mock_get_times_for_scan,
):

    expected_message = "No data found, no new report file to upload"
    mock_get_db_report_items.return_value = []
    bulk_upload_report_service.report_handler()

    mock_get_times_for_scan.assert_called_once()
    mock_get_db_report_items.assert_called_once()
    mock_get_db_report_items.assert_called_with(
        int(MOCK_START_REPORT_TIME.timestamp()),
        int(MOCK_END_REPORT_TIME.timestamp()),
    )

    mock_write_items_to_csv.assert_not_called()
    bulk_upload_report_service.s3_service.upload_file.assert_not_called()

    assert caplog.records[-1].msg == expected_message


def test_report_handler_with_items_uploads_summary_report_to_bucket(
    bulk_upload_report_service,
    mock_get_db_with_data,
    mock_write_summary_data_to_csv,
    mock_get_times_for_scan,
    caplog,
):
    expected_messages = [
        "Successfully processed daily ODS reports",
        "Successfully processed daily summary report",
        "Successfully processed daily report",
    ]

    mock_date_string_without_dashes = MOCK_END_REPORT_TIME.strftime("%Y%m%d")
    mock_date_string_with_dashes = MOCK_END_REPORT_TIME.strftime("%Y-%m-%d")

    bulk_upload_report_service.report_handler()

    mock_get_times_for_scan.assert_called_once()
    mock_get_db_with_data.assert_called_once_with(
        int(MOCK_START_REPORT_TIME.timestamp()),
        int(MOCK_END_REPORT_TIME.timestamp()),
    )

    mock_write_summary_data_to_csv.assert_called()

    calls = [
        call(
            s3_bucket_name=MOCK_STATISTICS_REPORT_BUCKET_NAME,
            file_key=f"daily_statistical_report_bulk_upload_summary_{mock_date_string_without_dashes}_uploaded_by_Y12345.csv",
            file_name=f"/tmp/daily_statistical_report_bulk_upload_summary_{mock_date_string_without_dashes}_uploaded_by_Y12345.csv",
        ),
        call(
            s3_bucket_name=MOCK_STATISTICS_REPORT_BUCKET_NAME,
            file_key=f"daily-reports/daily_statistical_report_bulk_upload_summary_{mock_date_string_without_dashes}.csv",
            file_name=f"/tmp/daily_statistical_report_bulk_upload_summary_{mock_date_string_without_dashes}.csv",
        ),
        call(
            s3_bucket_name=MOCK_STATISTICS_REPORT_BUCKET_NAME,
            file_key=f"daily-reports/{mock_date_string_with_dashes}/daily_report_{mock_date_string_without_dashes}.csv",
            file_name=f"daily_report_{mock_date_string_without_dashes}.csv",
        ),
    ]

    bulk_upload_report_service.s3_service.upload_file.assert_has_calls(calls)

    log_message_match = set(expected_messages).issubset(caplog.messages)

    assert log_message_match


def test_generate_individual_ods_report_creates_ods_report(
    bulk_upload_report_service, mock_write_summary_data_to_csv
):
    mock_ods_report_data = [MOCK_DATA_COMPLETE_UPLOAD, MOCK_DATA_FAILED_UPLOAD]
    expected = OdsReport(
        TEST_CURRENT_GP_ODS,
        1,
        0,
        0,
        {"File name not matching Lloyd George naming convention": 1},
    )
    actual = bulk_upload_report_service.generate_individual_ods_report(
        TEST_CURRENT_GP_ODS, mock_ods_report_data, MOCK_END_REPORT_TIME
    )

    assert actual.__dict__ == expected.__dict__
    bulk_upload_report_service.s3_service.upload_file.assert_called()
    mock_write_summary_data_to_csv.assert_called()


def test_generate_individual_ods_report_writes_csv_report(bulk_upload_report_service):
    mock_ods_report_data = [MOCK_DATA_COMPLETE_UPLOAD, MOCK_DATA_FAILED_UPLOAD]
    mock_date = 20120114
    mock_file_name = f"daily_statistical_report_bulk_upload_summary_{mock_date}_uploaded_by_{TEST_CURRENT_GP_ODS}.csv"

    bulk_upload_report_service.generate_individual_ods_report(
        TEST_CURRENT_GP_ODS,
        mock_ods_report_data,
        mock_date,
    )
    expected = readfile("expected_bulk_upload_report.csv")
    with open(f"/tmp/{mock_file_name}") as test_file:
        actual = test_file.read()
        assert expected == actual
    os.remove(f"/tmp/{mock_file_name}")

    bulk_upload_report_service.s3_service.upload_file.assert_called_with(
        s3_bucket_name=MOCK_STATISTICS_REPORT_BUCKET_NAME,
        file_key=f"{mock_file_name}",
        file_name=f"/tmp/{mock_file_name}",
    )


def test_generate_summary_report_with_two_ods_reports(bulk_upload_report_service):
    mock_ods_report_data = [
        MOCK_DATA_COMPLETE_UPLOAD,
        MOCK_DATA_FAILED_UPLOAD,
        MOCK_BULK_REPORT_TABLE_RESPONSE[0],
        MOCK_BULK_REPORT_TABLE_RESPONSE[2],
    ]
    mock_file_name = (
        f"daily_statistical_report_bulk_upload_summary_{MOCK_END_REPORT_TIME}.csv"
    )

    ods_reports = bulk_upload_report_service.generate_ods_reports(
        mock_ods_report_data, MOCK_END_REPORT_TIME
    )
    assert len(ods_reports) == 2
    bulk_upload_report_service.generate_summary_report(
        ods_reports, MOCK_END_REPORT_TIME
    )
    expected = readfile("expected_bulk_upload_summary_report.csv")
    with open(f"/tmp/{mock_file_name}") as test_file:
        actual = test_file.read()
        assert expected == actual
    os.remove(f"/tmp/{mock_file_name}")


def test_reports_count_individual_patients_success_and_failures(
    bulk_upload_report_service,
):
    mock_file_name = (
        f"daily_statistical_report_bulk_upload_summary_{MOCK_END_REPORT_TIME}.csv"
    )
    mock_ods_report_data = [
        MOCK_DATA_COMPLETE_UPLOAD,
        MOCK_DATA_FAILED_UPLOAD,
    ] + MOCK_BULK_REPORT_TABLE_RESPONSE

    ods_reports = bulk_upload_report_service.generate_ods_reports(
        mock_ods_report_data, MOCK_END_REPORT_TIME
    )

    bulk_upload_report_service.generate_summary_report(
        ods_reports, MOCK_END_REPORT_TIME
    )
    expected = readfile("expected_bulk_upload_summary_report.csv")
    with open(f"/tmp/{mock_file_name}") as test_file:
        actual = test_file.read()
        assert expected == actual
    os.remove(f"/tmp/{mock_file_name}")
