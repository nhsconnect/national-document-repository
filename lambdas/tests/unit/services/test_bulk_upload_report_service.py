from datetime import datetime
from unittest.mock import call

import pytest
from boto3.dynamodb.conditions import Attr
from freezegun import freeze_time
from services.bulk_upload_report_service import BulkUploadReportService, OdsReport
from tests.unit.conftest import (
    MOCK_BULK_REPORT_TABLE_NAME,
    TEST_CURRENT_GP_ODS,
    TEST_NHS_NUMBER,
    TEST_UUID,
)
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

MOCK_BULK_REPORT_TABLE_RESPONSE = [
    {
        "Timestamp": 1688395680,
        "Date": "2012-01-13",
        "NhsNumber": TEST_NHS_NUMBER,
        "FilePath": f"/{TEST_NHS_NUMBER}/1of1_Lloyd_George_Record_[NAME]_[{TEST_NHS_NUMBER}_[DOB].pdf",
        "UploaderOdsCode": "TEST",
        "UploadStatus": "complete",
        "ID": TEST_UUID,
        "PdsOdsCode": "TEST",
    },
    {
        "Timestamp": 1688395681,
        "Date": "2012-01-13",
        "NhsNumber": "9000000010",
        "FilePath": "/9000000010/1of1_Lloyd_George_Record_[NAME_2]_[9000000010]_[DOB].pdf",
        "UploaderOdsCode": "TEST",
        "FailureReason": "Could not find the given patient on PDS",
        "UploadStatus": "failed",
        "ID": TEST_UUID,
        "PdsOdsCode": "",
    },
]


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


def test_report_handler_no_items_return(
    mocker, set_env, bulk_upload_report_service, caplog
):
    mock_end_report_time = datetime(2012, 1, 14, 7, 0, 0, 0)
    mock_start_report_time = datetime(2012, 1, 13, 7, 0, 0, 0)
    mock_get_time = mocker.patch(
        "services.bulk_upload_report_service.BulkUploadReportService.get_times_for_scan",
        return_value=(mock_start_report_time, mock_end_report_time),
    )

    expected_message = "No data found, no new report file to upload"

    mock_get_db = mocker.patch(
        "services.bulk_upload_report_service.BulkUploadReportService.get_dynamodb_report_items",
        return_value=[],
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

    mock_write_csv.assert_not_called()
    bulk_upload_report_service.s3_service.upload_file.assert_not_called()

    assert caplog.records[-1].msg == expected_message


def test_report_handler_with_items(mocker, set_env, bulk_upload_report_service):
    mock_end_report_time = datetime(2012, 1, 14, 7, 0, 0, 0)
    mock_start_report_time = datetime(2012, 1, 13, 7, 0, 0, 0)
    mock_get_time = mocker.patch(
        "services.bulk_upload_report_service.BulkUploadReportService.get_times_for_scan",
        return_value=(mock_start_report_time, mock_end_report_time),
    )
    mock_get_db = mocker.patch(
        "services.bulk_upload_report_service.BulkUploadReportService.get_dynamodb_report_items",
        return_value=[MOCK_DATA_COMPLETE_UPLOAD],
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

    mock_write_csv.assert_called()

    bulk_upload_report_service.s3_service.upload_file.assert_called()
    # bulk_upload_report_service.s3_service.upload_file.assert_called_with(
    #     s3_bucket_name=MOCK_STATISTICS_REPORT_BUCKET_NAME,
    #     file_key=f"daily-reports/{mock_file_name}",
    #     file_name=f"/tmp/{mock_file_name}",
    # )


def test_generate_ods_report_object_creation(bulk_upload_report_service, mocker):
    mock_end_report_time = datetime(2012, 1, 14, 7, 0, 0, 0)
    mock_ods_report_data = [MOCK_DATA_COMPLETE_UPLOAD, MOCK_DATA_FAILED_UPLOAD]
    expected = OdsReport(
        TEST_CURRENT_GP_ODS,
        1,
        0,
        0,
        {"File name not matching Lloyd George naming convention": 1},
    )
    actual = bulk_upload_report_service.generate_individual_ods_report(
        TEST_CURRENT_GP_ODS, mock_ods_report_data, mock_end_report_time
    )

    assert actual.__eq__(expected)


def test_csv_written_with_correct_items(mocker, bulk_upload_report_service):
    mock_end_report_time = datetime(2012, 1, 14, 7, 0, 0, 0)
    mock_ods_report_data = [MOCK_DATA_COMPLETE_UPLOAD, MOCK_DATA_FAILED_UPLOAD]
    expected = OdsReport(
        TEST_CURRENT_GP_ODS,
        1,
        0,
        0,
        {"File name not matching Lloyd George naming convention": 1},
    )
    mock_write_csv = mocker.patch(
        "services.bulk_upload_report_service.BulkUploadReportService.write_items_to_csv"
    )
    bulk_upload_report_service.generate_individual_ods_report(
        TEST_CURRENT_GP_ODS, mock_ods_report_data, mock_end_report_time
    )
    extra_rows = [
        ["FailureReason", "File name not matching Lloyd George naming convention", 1]
    ]
    mock_write_csv.assert_called()
    mock_write_csv.assert_called_with(
        file_name=f"daily_statistical_report_bulk_upload_summary_{mock_end_report_time}_uploaded_by_{TEST_CURRENT_GP_ODS}.csv",
        total_successful=expected.total_successful,
        total_registered_elsewhere=expected.total_registered_elsewhere,
        total_suspended=expected.total_suspended,
        extra_rows=extra_rows,
    )


def test_generate_ods_reports_with_multiple_ods(bulk_upload_report_service):
    mock_end_report_time = datetime(2012, 1, 14, 7, 0, 0, 0)
    mock_ods_report_data = [
        MOCK_DATA_COMPLETE_UPLOAD,
        MOCK_DATA_FAILED_UPLOAD,
        MOCK_BULK_REPORT_TABLE_RESPONSE[0],
        MOCK_BULK_REPORT_TABLE_RESPONSE[1],
    ]

    actual = bulk_upload_report_service.generate_ods_reports(
        mock_ods_report_data, mock_end_report_time
    )
    assert len(actual) == 2


def test_generate_summary_report_with_two_ods_reports(
    mocker, bulk_upload_report_service
):
    mock_end_report_time = datetime(2012, 1, 14, 7, 0, 0, 0)
    mock_ods_report_data = [
        MOCK_DATA_COMPLETE_UPLOAD,
        MOCK_DATA_FAILED_UPLOAD,
        MOCK_BULK_REPORT_TABLE_RESPONSE[0],
        MOCK_BULK_REPORT_TABLE_RESPONSE[1],
    ]
    mock_write_csv = mocker.patch(
        "services.bulk_upload_report_service.BulkUploadReportService.write_items_to_csv"
    )

    ods_reports = bulk_upload_report_service.generate_ods_reports(
        mock_ods_report_data, mock_end_report_time
    )

    bulk_upload_report_service.generate_summary_report(
        ods_reports, mock_end_report_time
    )

    extra_rows = [
        ["FailureReason", "File name not matching Lloyd George naming convention", 1],
        ["FailureReason", "Could not find the given patient on PDS", 1],
        ["Success by ODS", "Y12345", 1],
        ["Success by ODS", "TEST", 1],
    ]
    mock_write_csv.assert_called()
    mock_write_csv.assert_called_with(
        file_name=f"daily_statistical_report_bulk_upload_summary_{mock_end_report_time}.csv",
        total_successful=2,
        total_registered_elsewhere=0,
        total_suspended=0,
        extra_rows=extra_rows,
    )
