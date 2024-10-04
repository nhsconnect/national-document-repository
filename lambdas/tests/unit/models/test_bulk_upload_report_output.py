from datetime import datetime

from enums.metadata_report import MetadataReport
from enums.upload_status import UploadStatus
from freezegun import freeze_time
from models.bulk_upload_report import BulkUploadReport
from models.bulk_upload_report_output import OdsReport, SummaryReport
from tests.unit.helpers.data.bulk_upload.dynamo_responses import (
    MOCK_REPORT_ITEMS_UPLOADER_1,
    MOCK_REPORT_ITEMS_UPLOADER_2,
    TEST_UPLOADER_ODS_1,
    TEST_UPLOADER_ODS_2,
)


@freeze_time("2024-01-01 12:00:00")
def get_timestamp():
    return datetime.now().strftime("%Y%m%d")


def test_report_base_get_sorted_sorts_successfully():
    to_sort = {
        ("9000000000", "2012-01-13"),
        ("9000000003", "2012-01-13"),
        ("9000000001", "2012-01-13"),
        ("9000000002", "2012-01-13"),
        ("9000000004", "2012-01-13"),
    }

    expected = [
        ("9000000000", "2012-01-13"),
        ("9000000001", "2012-01-13"),
        ("9000000002", "2012-01-13"),
        ("9000000003", "2012-01-13"),
        ("9000000004", "2012-01-13"),
    ]

    actual = OdsReport.get_sorted(to_sort)
    assert actual == expected


def test_report_base_get_sorted_returns_empty():
    to_sort = set()

    expected = []

    actual = OdsReport.get_sorted(to_sort)
    assert actual == expected


def test_ods_report_populate_report_populates_successfully():
    expected = {
        "generated_at": get_timestamp(),
        "total_successful": {
            ("9000000000", "2012-01-13"),
            ("9000000001", "2012-01-13"),
            ("9000000002", "2012-01-13"),
            ("9000000003", "2012-01-13"),
            ("9000000004", "2012-01-13"),
        },
        "total_registered_elsewhere": {("9000000004", "2012-01-13")},
        "total_suspended": {("9000000000", "2012-01-13")},
        "total_deceased": {
            ("9000000001", "2012-01-13", "Patient is deceased - INFORMAL")
        },
        "total_restricted": {("9000000002", "2012-01-13")},
        "report_items": MOCK_REPORT_ITEMS_UPLOADER_1,
        "failures_per_patient": {
            "9000000005": {
                "Date": "2012-01-13",
                "FailureReason": "Could not find the given patient on PDS",
                "Timestamp": 1688395681,
                "UploaderOdsCode": "Y12345",
            },
            "9000000006": {
                "Date": "2012-01-13",
                "FailureReason": "Could not find the given patient on PDS",
                "Timestamp": 1688395681,
                "UploaderOdsCode": "Y12345",
            },
            "9000000007": {
                "Date": "2012-01-13",
                "FailureReason": "Lloyd George file already exists",
                "Timestamp": 1688395681,
                "UploaderOdsCode": "Y12345",
            },
        },
        "unique_failures": {
            "Could not find the given patient on PDS": 2,
            "Lloyd George file already exists": 1,
        },
        "uploader_ods_code": TEST_UPLOADER_ODS_1,
    }

    actual = OdsReport(
        get_timestamp(),
        TEST_UPLOADER_ODS_1,
        MOCK_REPORT_ITEMS_UPLOADER_1,
    ).__dict__

    assert actual == expected


def test_ods_report_process_failed_report_item_handles_failures():
    old_time_stamp = 1698661500
    new_time_stamp = 1698661501
    old_failure_reason = "old reason"
    newest_failure_reason = "new reason"

    test_items = [
        BulkUploadReport(
            nhs_number="9000000009",
            timestamp=old_time_stamp,
            date="2023-10-30",
            upload_status=UploadStatus.FAILED,
            file_path="/9000000009/1of1_Lloyd_George_Record_[Joe Bloggs]_[9000000009]_[25-12-2019].pdf",
            failure_reason=old_failure_reason,
            pds_ods_code=TEST_UPLOADER_ODS_1,
            uploader_ods_code=TEST_UPLOADER_ODS_1,
        )
    ]

    new_failed_item = BulkUploadReport(
        nhs_number="9000000009",
        timestamp=new_time_stamp,
        date="2023-10-30",
        upload_status=UploadStatus.FAILED,
        file_path="/9000000009/1of1_Lloyd_George_Record_[Joe Bloggs]_[9000000009]_[25-12-2019].pdf",
        failure_reason=newest_failure_reason,
        pds_ods_code=TEST_UPLOADER_ODS_1,
        uploader_ods_code=TEST_UPLOADER_ODS_1,
    )

    expected = {
        "9000000009": {
            "Date": "2023-10-30",
            "FailureReason": old_failure_reason,
            "Timestamp": old_time_stamp,
            "UploaderOdsCode": TEST_UPLOADER_ODS_1,
        }
    }

    report = OdsReport(
        get_timestamp(),
        TEST_UPLOADER_ODS_1,
        test_items,
    )
    report.report_items = test_items

    actual = report.failures_per_patient
    assert actual == expected

    report.process_failed_report_item(new_failed_item)
    expected = {
        "9000000009": {
            "Date": "2023-10-30",
            "FailureReason": newest_failure_reason,
            "Timestamp": new_time_stamp,
            "UploaderOdsCode": TEST_UPLOADER_ODS_1,
        }
    }

    actual = report.failures_per_patient
    assert actual == expected


def test_ods_report_get_unsuccessful_reasons_data_rows_returns_correct_rows():
    report = OdsReport(
        get_timestamp(),
        TEST_UPLOADER_ODS_1,
        MOCK_REPORT_ITEMS_UPLOADER_1,
    )

    expected = [
        [MetadataReport.FailureReason, "Could not find the given patient on PDS", 2],
        [MetadataReport.FailureReason, "Lloyd George file already exists", 1],
    ]

    actual = report.get_unsuccessful_reasons_data_rows()

    assert actual == expected


def test_ods_report_populate_report_empty_list_populates_successfully():
    expected = {
        "generated_at": get_timestamp(),
        "total_successful": set(),
        "total_registered_elsewhere": set(),
        "total_suspended": set(),
        "total_deceased": set(),
        "total_restricted": set(),
        "report_items": [],
        "failures_per_patient": {},
        "unique_failures": {},
        "uploader_ods_code": TEST_UPLOADER_ODS_1,
    }

    actual = OdsReport(
        get_timestamp(),
        TEST_UPLOADER_ODS_1,
        [],
    ).__dict__

    assert actual == expected


def test_ods_report_populate_report_returns_correct_statistics():
    actual = OdsReport(
        get_timestamp(),
        TEST_UPLOADER_ODS_1,
        MOCK_REPORT_ITEMS_UPLOADER_1,
    )

    assert actual.get_total_successful_count() == 5
    assert actual.get_total_deceased_count() == 1
    assert actual.get_total_suspended_count() == 1
    assert actual.get_total_restricted_count() == 1
    assert actual.get_total_registered_elsewhere_count() == 1


def test_ods_report_populate_report_empty_list_returns_correct_statistics():
    actual = OdsReport(
        get_timestamp(),
        TEST_UPLOADER_ODS_1,
        [],
    )

    assert actual.get_total_successful_count() == 0
    assert actual.get_total_deceased_count() == 0
    assert actual.get_total_suspended_count() == 0
    assert actual.get_total_restricted_count() == 0
    assert actual.get_total_registered_elsewhere_count() == 0
    assert sorted(actual.get_total_successful_nhs_numbers()) == []
    assert actual.get_sorted(actual.total_successful) == []


def test_summary_report_populate_report_populates_successfully():
    test_uploader_reports = [
        OdsReport(
            get_timestamp(),
            TEST_UPLOADER_ODS_1,
            MOCK_REPORT_ITEMS_UPLOADER_1,
        ),
        OdsReport(
            get_timestamp(),
            TEST_UPLOADER_ODS_2,
            MOCK_REPORT_ITEMS_UPLOADER_2,
        ),
    ]

    expected = {
        "generated_at": get_timestamp(),
        "total_successful": {
            ("9000000000", "2012-01-13"),
            ("9000000001", "2012-01-13"),
            ("9000000002", "2012-01-13"),
            ("9000000003", "2012-01-13"),
            ("9000000004", "2012-01-13"),
            ("9000000009", "2012-01-13"),
            ("9000000010", "2012-01-13"),
            ("9000000011", "2012-01-13"),
            ("9000000012", "2012-01-13"),
            ("9000000013", "2012-01-13"),
        },
        "total_registered_elsewhere": {
            ("9000000004", "2012-01-13"),
            ("9000000012", "2012-01-13"),
        },
        "total_suspended": {("9000000000", "2012-01-13"), ("9000000009", "2012-01-13")},
        "total_deceased": {
            ("9000000001", "2012-01-13", "Patient is deceased - INFORMAL"),
            ("9000000010", "2012-01-13", "Patient is deceased - FORMAL"),
        },
        "total_restricted": {
            ("9000000002", "2012-01-13"),
            ("9000000011", "2012-01-13"),
        },
        "ods_reports": test_uploader_reports,
        "success_summary": [
            ["Success by ODS", "Y12345", 5],
            ["Success by ODS", "Z12345", 5],
        ],
        "reason_summary": [
            ["FailureReason for Y12345", "Could not find the given patient on PDS", 2],
            ["FailureReason for Y12345", "Lloyd George file already exists", 1],
            ["FailureReason for Z12345", "Could not find the given patient on PDS", 2],
            ["FailureReason for Z12345", "Lloyd George file already exists", 1],
        ],
    }

    actual = SummaryReport(
        generated_at=get_timestamp(), ods_reports=test_uploader_reports
    ).__dict__

    assert actual == expected


def test_summary_report_populate_report_empty_reports_objects_populate_successfully():
    test_uploader_reports = [
        OdsReport(
            get_timestamp(),
            TEST_UPLOADER_ODS_1,
            [],
        ),
        OdsReport(
            get_timestamp(),
            TEST_UPLOADER_ODS_2,
            [],
        ),
    ]

    expected = {
        "generated_at": get_timestamp(),
        "total_successful": set(),
        "total_registered_elsewhere": set(),
        "total_suspended": set(),
        "total_deceased": set(),
        "total_restricted": set(),
        "ods_reports": test_uploader_reports,
        "success_summary": [
            ["Success by ODS", "Y12345", 0],
            ["Success by ODS", "Z12345", 0],
        ],
        "reason_summary": [],
    }

    actual = SummaryReport(
        generated_at=get_timestamp(), ods_reports=test_uploader_reports
    ).__dict__

    assert actual == expected


def test_summary_report_populate_report_no_report_objects_populate_successfully():
    expected = {
        "generated_at": get_timestamp(),
        "total_successful": set(),
        "total_registered_elsewhere": set(),
        "total_suspended": set(),
        "total_deceased": set(),
        "total_restricted": set(),
        "ods_reports": [],
        "success_summary": [["Success by ODS", "No ODS codes found", 0]],
        "reason_summary": [],
    }

    actual = SummaryReport(generated_at=get_timestamp(), ods_reports=[]).__dict__

    assert actual == expected
