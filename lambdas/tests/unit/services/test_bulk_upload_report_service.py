import os
from datetime import datetime
from unittest.mock import call

import pytest
from boto3.dynamodb.conditions import Attr
from freezegun import freeze_time
from services.bulk_upload_report_service import BulkUploadReportService
from tests.unit.conftest import MOCK_BULK_REPORT_TABLE_NAME, MOCK_STAGING_STORE_BUCKET
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


@pytest.fixture()
def bulk_upload_report_service(mocker):
    patched_bulk_upload_report_service = BulkUploadReportService()
    mocker.patch.object(patched_bulk_upload_report_service, "db_service")
    mocker.patch.object(patched_bulk_upload_report_service, "s3_service")
    yield patched_bulk_upload_report_service


@freeze_time("2012-01-14 7:20:01")
def test_get_time_for_scan_after_7am(bulk_upload_report_service):
    expected_end_report_time = datetime(2012, 1, 14, 7, 0, 0, 0)
    expected_start_report_time = datetime(2012, 1, 13, 7, 0, 0, 0)

    (
        actual_start_time,
        actual_end_time,
    ) = bulk_upload_report_service.get_times_for_scan()

    assert expected_start_report_time == actual_start_time
    assert expected_end_report_time == actual_end_time


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


def test_write_items_to_csv(bulk_upload_report_service):
    items = [MOCK_DATA_COMPLETE_UPLOAD, MOCK_DATA_FAILED_UPLOAD]
    expected = readfile("expected_bulk_upload_report.csv")

    bulk_upload_report_service.write_items_to_csv(items, "test_file")

    with open("test_file") as test_file:
        actual = test_file.read()
        assert expected == actual
    os.remove("test_file")


def test_write_empty_file_to_txt(bulk_upload_report_service):
    bulk_upload_report_service.write_empty_report("test_file")

    with open("test_file") as test_file:
        file_content = test_file.read()
    assert file_content == "No data was found for this timeframe"
    os.remove("test_file")


def test_get_dynamo_data_2_calls(mocker, set_env, bulk_upload_report_service):
    mock_start_time = 1688395630
    mock_end_time = 1688195630
    mock_filter = Attr("Timestamp").gt(mock_start_time) & Attr("Timestamp").lt(
        mock_end_time
    )
    mock_last_key = {"FileName": "Screenshot 2023-08-15 at 16.17.56.png"}
    bulk_upload_report_service.db_service.scan_table.side_effect = [
        MOCK_RESPONSE_WITH_LAST_KEY,
        MOCK_RESPONSE,
    ]

    actual = bulk_upload_report_service.get_dynamodb_report_items(
        mock_start_time, mock_end_time
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


def test_get_dynamo_data_with_no_start_key(mocker, set_env, bulk_upload_report_service):
    mock_start_time = 1688395630
    mock_end_time = 1688195630
    mock_filter = Attr("Timestamp").gt(mock_start_time) & Attr("Timestamp").lt(
        mock_end_time
    )
    bulk_upload_report_service.db_service.scan_table.side_effect = [MOCK_RESPONSE]

    actual = bulk_upload_report_service.get_dynamodb_report_items(
        mock_start_time, mock_end_time
    )

    assert actual == EXPECTED_RESPONSE
    bulk_upload_report_service.db_service.scan_table.assert_called_once()
    bulk_upload_report_service.db_service.scan_table.assert_called_with(
        MOCK_BULK_REPORT_TABLE_NAME, filter_expression=mock_filter
    )


def test_get_dynamo_data_with_no_items(mocker, set_env, bulk_upload_report_service):
    mock_start_time = 1688395630
    mock_end_time = 1688195630
    bulk_upload_report_service.db_service.scan_table.side_effect = [MOCK_EMPTY_RESPONSE]

    actual = bulk_upload_report_service.get_dynamodb_report_items(
        mock_start_time, mock_end_time
    )

    assert actual == []
    bulk_upload_report_service.db_service.scan_table.assert_called_once()


def test_get_dynamo_data_with_bad_response(mocker, set_env, bulk_upload_report_service):
    mock_start_time = 1688395630
    mock_end_time = 1688195630
    bulk_upload_report_service.db_service.scan_table.side_effect = [UNEXPECTED_RESPONSE]

    actual = bulk_upload_report_service.get_dynamodb_report_items(
        mock_start_time, mock_end_time
    )

    assert actual is None
    bulk_upload_report_service.db_service.scan_table.assert_called_once()


def test_report_handler_no_items_return(mocker, set_env, bulk_upload_report_service):
    mock_end_report_time = datetime(2012, 1, 14, 7, 0, 0, 0)
    mock_start_report_time = datetime(2012, 1, 13, 7, 0, 0, 0)
    f"Bulk upload report for {str(mock_start_report_time)} to {str(mock_end_report_time)}.txt"
    mock_get_time = mocker.patch(
        "services.bulk_upload_report_service.BulkUploadReportService.get_times_for_scan",
        return_value=(mock_start_report_time, mock_end_report_time),
    )
    mocker.patch(
        "services.bulk_upload_report_service.BulkUploadReportService.write_empty_report"
    )
    mock_get_db = mocker.patch(
        "services.bulk_upload_report_service.BulkUploadReportService.get_dynamodb_report_items",
        return_value=[],
    )

    bulk_upload_report_service.report_handler()

    mock_get_time.assert_called_once()
    mock_get_db.assert_called_once()
    mock_get_db.assert_called_with(
        int(mock_start_report_time.timestamp()),
        int(mock_end_report_time.timestamp()),
    )

    bulk_upload_report_service.write_empty_report.assert_not_called()
    bulk_upload_report_service.s3_service.upload_file.assert_not_called()
    # mock_write_empty_csv.assert_called_once()
    # bulk_upload_report_service.s3_service.upload_file.assert_called_with(
    #     s3_bucket_name=MOCK_STAGING_STORE_BUCKET,
    #     file_key=f"reports/{mock_file_name}",
    #     file_name=f"/tmp/{mock_file_name}",
    # )


def test_report_handler_with_items(mocker, set_env, bulk_upload_report_service):
    mock_end_report_time = datetime(2012, 1, 14, 7, 0, 0, 0)
    mock_start_report_time = datetime(2012, 1, 13, 7, 0, 0, 0)
    mock_file_name = f"Bulk upload report for {str(mock_start_report_time)} to {str(mock_end_report_time)}.csv"
    mock_get_time = mocker.patch(
        "services.bulk_upload_report_service.BulkUploadReportService.get_times_for_scan",
        return_value=(mock_start_report_time, mock_end_report_time),
    )
    mock_write_empty_csv = mocker.patch(
        "services.bulk_upload_report_service.BulkUploadReportService.write_empty_report"
    )
    mock_get_db = mocker.patch(
        "services.bulk_upload_report_service.BulkUploadReportService.get_dynamodb_report_items",
        return_value=[{"test": "dsfsf"}],
    )
    mock_write_csv = mocker.patch(
        "services.bulk_upload_report_service.BulkUploadReportService.write_items_to_csv"
    )

    bulk_upload_report_service.report_handler()

    mock_get_time.assert_called_once()
    mock_get_db.assert_called_once()
    mock_get_db.assert_called_with(
        int(mock_start_report_time.timestamp()),
        int(mock_end_report_time.timestamp()),
    )
    mock_write_empty_csv.assert_not_called()
    mock_write_csv.assert_called_once()
    mock_write_csv.assert_called_with([{"test": "dsfsf"}], f"/tmp/{mock_file_name}")
    bulk_upload_report_service.s3_service.upload_file.assert_called_with(
        s3_bucket_name=MOCK_STAGING_STORE_BUCKET,
        file_key=f"reports/{mock_file_name}",
        file_name=f"/tmp/{mock_file_name}",
    )
