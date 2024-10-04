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
)
from tests.unit.helpers.data.bulk_upload.dynamo_responses import (
    MOCK_REPORT_ITEMS_ALL,
    MOCK_REPORT_ITEMS_UPLOADER_1,
    MOCK_REPORT_RESPONSE_ALL,
    MOCK_REPORT_RESPONSE_ALL_WITH_LAST_KEY,
    TEST_UPLOADER_ODS_1,
    TEST_UPLOADER_ODS_2,
)
from tests.unit.helpers.data.bulk_upload.test_data import readfile
from tests.unit.helpers.data.dynamo_scan_response import (
    MOCK_EMPTY_RESPONSE,
    UNEXPECTED_RESPONSE,
)
from utils.utilities import to_date_folder_name

MOCK_END_REPORT_TIME = datetime(2012, 1, 14, 7, 0, 0, 0)
MOCK_START_REPORT_TIME = datetime(2012, 1, 13, 7, 0, 0, 0)
MOCK_TIMESTAMP = MOCK_START_REPORT_TIME.strftime("%Y%m%d")


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
        return_value=MOCK_REPORT_ITEMS_ALL,
    )


@pytest.fixture
def mock_get_times_for_scan(bulk_upload_report_service, mocker):
    mock_date_folder_name = to_date_folder_name(MOCK_TIMESTAMP)
    bulk_upload_report_service.generated_on = MOCK_TIMESTAMP
    bulk_upload_report_service.s3_key_prefix = f"daily-reports/{mock_date_folder_name}"
    yield mocker.patch.object(
        bulk_upload_report_service,
        "get_times_for_scan",
        return_value=(MOCK_START_REPORT_TIME, MOCK_END_REPORT_TIME),
    )


@pytest.fixture
def mock_filter(mocker):
    mock_filter = Attr("Timestamp").gt(MOCK_START_REPORT_TIME) & Attr("Timestamp").lt(
        MOCK_END_REPORT_TIME
    )

    mocker.patch("boto3.dynamodb.conditions.And", return_value=mock_filter)

    yield mock_filter


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


def test_get_dynamo_data_2_calls(bulk_upload_report_service, mock_filter):
    mock_last_key = {
        "FilePath": "/9000000010/2of2_Lloyd_George_Record_[NAME_2]_[9000000010]_[DOB].pdf"
    }
    bulk_upload_report_service.db_service.scan_table.side_effect = [
        MOCK_REPORT_RESPONSE_ALL_WITH_LAST_KEY,
        MOCK_REPORT_RESPONSE_ALL,
    ]

    actual = bulk_upload_report_service.get_dynamodb_report_items(
        int(MOCK_START_REPORT_TIME.timestamp()), int(MOCK_END_REPORT_TIME.timestamp())
    )

    assert actual == MOCK_REPORT_ITEMS_ALL * 2
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


def test_get_dynamo_data_handles_invalid_dynamo_data(
    bulk_upload_report_service, mock_filter, caplog
):
    invalid_data = {
        "Timestamp": 1688395680,
        "Date": "2012-01-13",
        "FailureReason": "Lloyd George file already exists",
        "UploadStatus": "failed",
    }
    mock_response = {"Items": [invalid_data, MOCK_REPORT_RESPONSE_ALL["Items"][1]]}
    expected_message = "Failed to parse bulk update report dynamo item"

    bulk_upload_report_service.db_service.scan_table.side_effect = [
        mock_response,
    ]

    actual = bulk_upload_report_service.get_dynamodb_report_items(
        int(MOCK_START_REPORT_TIME.timestamp()), int(MOCK_END_REPORT_TIME.timestamp())
    )

    assert actual == [MOCK_REPORT_ITEMS_ALL[1]]
    assert expected_message in caplog.records[-1].msg


def test_get_dynamo_data_with_no_start_key(bulk_upload_report_service, mock_filter):
    bulk_upload_report_service.db_service.scan_table.side_effect = [
        MOCK_REPORT_RESPONSE_ALL
    ]

    actual = bulk_upload_report_service.get_dynamodb_report_items(
        int(MOCK_START_REPORT_TIME.timestamp()), int(MOCK_END_REPORT_TIME.timestamp())
    )

    assert actual == MOCK_REPORT_ITEMS_ALL
    bulk_upload_report_service.db_service.scan_table.assert_called_once()
    bulk_upload_report_service.db_service.scan_table.assert_called_with(
        MOCK_BULK_REPORT_TABLE_NAME, filter_expression=mock_filter
    )


def test_get_dynamo_data_with_no_items_returns_empty_list(bulk_upload_report_service):
    bulk_upload_report_service.db_service.scan_table.side_effect = [MOCK_EMPTY_RESPONSE]

    actual = bulk_upload_report_service.get_dynamodb_report_items(
        int(MOCK_START_REPORT_TIME.timestamp()), int(MOCK_END_REPORT_TIME.timestamp())
    )

    assert actual == []
    bulk_upload_report_service.db_service.scan_table.assert_called_once()


def test_get_dynamo_data_with_bad_response_returns_empty_list(
    bulk_upload_report_service,
):
    bulk_upload_report_service.db_service.scan_table.side_effect = [UNEXPECTED_RESPONSE]

    actual = bulk_upload_report_service.get_dynamodb_report_items(
        int(MOCK_START_REPORT_TIME.timestamp()), int(MOCK_END_REPORT_TIME.timestamp())
    )

    assert actual == []
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
            file_key=f"daily-reports/2012-01-13/daily_statistical_report_bulk_upload_ods_summary_{MOCK_TIMESTAMP}_uploaded_by_Y12345.csv",
            file_name=f"/tmp/daily_statistical_report_bulk_upload_ods_summary_{MOCK_TIMESTAMP}_uploaded_by_Y12345.csv",
        ),
        call(
            s3_bucket_name=MOCK_STATISTICS_REPORT_BUCKET_NAME,
            file_key=f"daily-reports/2012-01-13/daily_statistical_report_bulk_upload_ods_summary_{MOCK_TIMESTAMP}_uploaded_by_Z12345.csv",
            file_name=f"/tmp/daily_statistical_report_bulk_upload_ods_summary_{MOCK_TIMESTAMP}_uploaded_by_Z12345.csv",
        ),
        call(
            s3_bucket_name=MOCK_STATISTICS_REPORT_BUCKET_NAME,
            file_key=f"daily-reports/2012-01-13/daily_statistical_report_bulk_upload_summary_{MOCK_TIMESTAMP}.csv",
            file_name=f"/tmp/daily_statistical_report_bulk_upload_summary_{MOCK_TIMESTAMP}.csv",
        ),
        call(
            s3_bucket_name=MOCK_STATISTICS_REPORT_BUCKET_NAME,
            file_key=f"daily-reports/2012-01-13/daily_statistical_report_entire_bulk_upload_{str(MOCK_START_REPORT_TIME)}_to_{str(MOCK_END_REPORT_TIME)}.csv",
            file_name=f"/tmp/daily_statistical_report_entire_bulk_upload_{str(MOCK_START_REPORT_TIME)}_to_{str(MOCK_END_REPORT_TIME)}.csv",
        ),
        call(
            s3_bucket_name=MOCK_STATISTICS_REPORT_BUCKET_NAME,
            file_key=f"daily-reports/2012-01-13/daily_statistical_report_bulk_upload_success_{MOCK_TIMESTAMP}.csv",
            file_name=f"/tmp/daily_statistical_report_bulk_upload_success_{MOCK_TIMESTAMP}.csv",
        ),
        call(
            s3_bucket_name=MOCK_STATISTICS_REPORT_BUCKET_NAME,
            file_key=f"daily-reports/2012-01-13/daily_statistical_report_bulk_upload_suspended_{MOCK_TIMESTAMP}.csv",
            file_name=f"/tmp/daily_statistical_report_bulk_upload_suspended_{MOCK_TIMESTAMP}.csv",
        ),
        call(
            s3_bucket_name=MOCK_STATISTICS_REPORT_BUCKET_NAME,
            file_key=f"daily-reports/2012-01-13/daily_statistical_report_bulk_upload_deceased_{MOCK_TIMESTAMP}.csv",
            file_name=f"/tmp/daily_statistical_report_bulk_upload_deceased_{MOCK_TIMESTAMP}.csv",
        ),
        call(
            s3_bucket_name=MOCK_STATISTICS_REPORT_BUCKET_NAME,
            file_key=f"daily-reports/2012-01-13/daily_statistical_report_bulk_upload_restricted_{MOCK_TIMESTAMP}.csv",
            file_name=f"/tmp/daily_statistical_report_bulk_upload_restricted_{MOCK_TIMESTAMP}.csv",
        ),
        call(
            s3_bucket_name=MOCK_STATISTICS_REPORT_BUCKET_NAME,
            file_key=f"daily-reports/2012-01-13/daily_statistical_report_bulk_upload_rejected_{MOCK_TIMESTAMP}.csv",
            file_name=f"/tmp/daily_statistical_report_bulk_upload_rejected_{MOCK_TIMESTAMP}.csv",
        ),
    ]

    bulk_upload_report_service.s3_service.upload_file.assert_has_calls(
        calls, any_order=False
    )

    log_message_match = set(expected_messages).issubset(caplog.messages)

    assert log_message_match


def test_generate_individual_ods_report_creates_ods_report(
    bulk_upload_report_service, mock_write_summary_data_to_csv, mock_get_times_for_scan
):
    expected = OdsReport(
        MOCK_TIMESTAMP,
        TEST_UPLOADER_ODS_1,
        MOCK_REPORT_ITEMS_UPLOADER_1,
    )

    actual = bulk_upload_report_service.generate_individual_ods_report(
        TEST_UPLOADER_ODS_1, MOCK_REPORT_ITEMS_UPLOADER_1
    )

    assert actual.__dict__ == expected.__dict__

    mock_write_summary_data_to_csv.assert_called_with(
        file_name=f"daily_statistical_report_bulk_upload_ods_summary_{MOCK_TIMESTAMP}_uploaded_by_{TEST_CURRENT_GP_ODS}.csv",
        total_successful=5,
        total_registered_elsewhere=1,
        total_suspended=1,
        extra_rows=[
            ["FailureReason", "Could not find the given patient on PDS", 2],
            ["FailureReason", "Lloyd George file already exists", 1],
        ],
    )
    bulk_upload_report_service.s3_service.upload_file.assert_called()


def test_generate_individual_ods_report_writes_csv_report(
    bulk_upload_report_service, mock_get_times_for_scan
):
    mock_file_name = f"daily_statistical_report_bulk_upload_ods_summary_{MOCK_TIMESTAMP}_uploaded_by_{TEST_CURRENT_GP_ODS}.csv"

    bulk_upload_report_service.generate_individual_ods_report(
        TEST_UPLOADER_ODS_1, MOCK_REPORT_ITEMS_UPLOADER_1
    )
    expected = readfile("expected_ods_report_for_uploader_1.csv")
    with open(f"/tmp/{mock_file_name}") as test_file:
        actual = test_file.read()
        assert expected == actual
    os.remove(f"/tmp/{mock_file_name}")

    bulk_upload_report_service.s3_service.upload_file.assert_called_with(
        s3_bucket_name=MOCK_STATISTICS_REPORT_BUCKET_NAME,
        file_key=f"daily-reports/2012-01-13/{mock_file_name}",
        file_name=f"/tmp/{mock_file_name}",
    )


def test_generate_ods_reports_writes_multiple_ods_reports(
    bulk_upload_report_service, mock_get_times_for_scan
):
    mock_file_name_uploader_1 = (
        f"daily_statistical_report_bulk_upload_ods_summary_{MOCK_TIMESTAMP}"
        f"_uploaded_by_{TEST_UPLOADER_ODS_1}.csv"
    )
    mock_file_name_uploader_2 = (
        f"daily_statistical_report_bulk_upload_ods_summary_{MOCK_TIMESTAMP}"
        f"_uploaded_by_{TEST_UPLOADER_ODS_2}.csv"
    )

    bulk_upload_report_service.generate_ods_reports(
        MOCK_REPORT_ITEMS_ALL,
    )
    expected = readfile("expected_ods_report_for_uploader_1.csv")
    with open(f"/tmp/{mock_file_name_uploader_1}") as test_file:
        actual = test_file.read()
        assert expected == actual
    os.remove(f"/tmp/{mock_file_name_uploader_1}")

    expected = readfile("expected_ods_report_for_uploader_2.csv")
    with open(f"/tmp/{mock_file_name_uploader_2}") as test_file:
        actual = test_file.read()
        assert expected == actual
    os.remove(f"/tmp/{mock_file_name_uploader_2}")


def test_generate_summary_report_with_two_ods_reports(
    bulk_upload_report_service, mock_get_times_for_scan
):
    mock_file_name = (
        f"daily_statistical_report_bulk_upload_summary_{MOCK_TIMESTAMP}.csv"
    )

    ods_reports = bulk_upload_report_service.generate_ods_reports(MOCK_REPORT_ITEMS_ALL)
    assert len(ods_reports) == 2
    bulk_upload_report_service.generate_summary_report(ods_reports)
    expected = readfile("expected_bulk_upload_summary_report.csv")
    with open(f"/tmp/{mock_file_name}") as test_file:
        actual = test_file.read()
        assert expected == actual
    os.remove(f"/tmp/{mock_file_name}")


def test_generate_success_report_writes_csv(
    bulk_upload_report_service, mock_get_times_for_scan
):
    mock_file_name = (
        f"daily_statistical_report_bulk_upload_success_{MOCK_TIMESTAMP}.csv"
    )

    test_ods_reports = bulk_upload_report_service.generate_ods_reports(
        MOCK_REPORT_ITEMS_ALL,
    )

    bulk_upload_report_service.generate_success_report(test_ods_reports)

    expected = readfile("expected_success_report.csv")
    with open(f"/tmp/{mock_file_name}") as test_file:
        actual = test_file.read()
        assert expected == actual
    os.remove(f"/tmp/{mock_file_name}")

    bulk_upload_report_service.s3_service.upload_file.assert_called_with(
        s3_bucket_name=MOCK_STATISTICS_REPORT_BUCKET_NAME,
        file_key=f"daily-reports/2012-01-13/{mock_file_name}",
        file_name=f"/tmp/{mock_file_name}",
    )


def test_generate_suspended_report_writes_csv(
    bulk_upload_report_service, mock_get_times_for_scan
):
    mock_file_name = (
        f"daily_statistical_report_bulk_upload_suspended_{MOCK_TIMESTAMP}.csv"
    )

    test_ods_reports = bulk_upload_report_service.generate_ods_reports(
        MOCK_REPORT_ITEMS_ALL,
    )

    bulk_upload_report_service.generate_suspended_report(test_ods_reports)

    expected = readfile("expected_suspended_report.csv")
    with open(f"/tmp/{mock_file_name}") as test_file:
        actual = test_file.read()
        assert expected == actual
    os.remove(f"/tmp/{mock_file_name}")

    bulk_upload_report_service.s3_service.upload_file.assert_called_with(
        s3_bucket_name=MOCK_STATISTICS_REPORT_BUCKET_NAME,
        file_key=f"daily-reports/2012-01-13/{mock_file_name}",
        file_name=f"/tmp/{mock_file_name}",
    )


def test_generate_deceased_report_writes_csv(
    bulk_upload_report_service, mock_get_times_for_scan
):
    mock_file_name = (
        f"daily_statistical_report_bulk_upload_deceased_{MOCK_TIMESTAMP}.csv"
    )

    test_ods_reports = bulk_upload_report_service.generate_ods_reports(
        MOCK_REPORT_ITEMS_ALL,
    )

    bulk_upload_report_service.generate_deceased_report(test_ods_reports)

    expected = readfile("expected_deceased_report.csv")
    with open(f"/tmp/{mock_file_name}") as test_file:
        actual = test_file.read()
        assert expected == actual
    os.remove(f"/tmp/{mock_file_name}")

    bulk_upload_report_service.s3_service.upload_file.assert_called_with(
        s3_bucket_name=MOCK_STATISTICS_REPORT_BUCKET_NAME,
        file_key=f"daily-reports/2012-01-13/{mock_file_name}",
        file_name=f"/tmp/{mock_file_name}",
    )


def test_generate_restricted_report_writes_csv(
    bulk_upload_report_service, mock_get_times_for_scan
):
    mock_file_name = (
        f"daily_statistical_report_bulk_upload_restricted_{MOCK_TIMESTAMP}.csv"
    )

    test_ods_reports = bulk_upload_report_service.generate_ods_reports(
        MOCK_REPORT_ITEMS_ALL,
    )

    bulk_upload_report_service.generate_restricted_report(test_ods_reports)

    expected = readfile("expected_restricted_report.csv")
    with open(f"/tmp/{mock_file_name}") as test_file:
        actual = test_file.read()
        assert expected == actual
    os.remove(f"/tmp/{mock_file_name}")

    bulk_upload_report_service.s3_service.upload_file.assert_called_with(
        s3_bucket_name=MOCK_STATISTICS_REPORT_BUCKET_NAME,
        file_key=f"daily-reports/2012-01-13/{mock_file_name}",
        file_name=f"/tmp/{mock_file_name}",
    )


def test_generate_rejected_report_writes_csv(
    bulk_upload_report_service, mock_get_times_for_scan
):
    mock_file_name = (
        f"daily_statistical_report_bulk_upload_rejected_{MOCK_TIMESTAMP}.csv"
    )

    test_ods_reports = bulk_upload_report_service.generate_ods_reports(
        MOCK_REPORT_ITEMS_ALL,
    )

    bulk_upload_report_service.generate_rejected_report(test_ods_reports)

    expected = readfile("expected_rejected_report.csv")
    with open(f"/tmp/{mock_file_name}") as test_file:
        actual = test_file.read()
        assert expected == actual
    os.remove(f"/tmp/{mock_file_name}")

    bulk_upload_report_service.s3_service.upload_file.assert_called_with(
        s3_bucket_name=MOCK_STATISTICS_REPORT_BUCKET_NAME,
        file_key=f"daily-reports/2012-01-13/{mock_file_name}",
        file_name=f"/tmp/{mock_file_name}",
    )
