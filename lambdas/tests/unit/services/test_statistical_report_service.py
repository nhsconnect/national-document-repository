from random import shuffle

import polars as pl
import pytest
from freezegun import freeze_time
from polars.testing import assert_frame_equal
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from services.statistical_report_service import StatisticalReportService
from unit.helpers.data.statistic.mock_statistic_data import (
    build_random_organisation_data,
    build_random_record_store_data,
)
from utils.polars_utils import CastDecimalToFloat


@pytest.fixture
def mock_service(set_env, mock_s3_service, mock_dynamodb_service):
    return StatisticalReportService()


@pytest.fixture
def mock_s3_service(mocker):
    patched_instance = mocker.patch(
        "services.statistical_report_service.S3Service", spec=S3Service
    ).return_value

    yield patched_instance


@pytest.fixture
def mock_dynamodb_service(mocker):
    patched_instance = mocker.patch(
        "services.statistical_report_service.DynamoDBService", spec=DynamoDBService
    ).return_value

    yield patched_instance


@freeze_time("2024-06-06T18:00:00Z")
def test_datetime_correctly_configured_during_initialise(set_env):
    service = StatisticalReportService()

    assert service.report_period == [
        "20240530",
        "20240531",
        "20240601",
        "20240602",
        "20240603",
        "20240604",
        "20240605",
    ]
    assert service.date_period_on_output_filename == "20240530-20240605"


def test_summarise_record_store_data(mock_service):
    mock_data_H81109 = build_random_record_store_data(
        "H81109", ["20240601", "20240603", "20240604", "20240605", "20240607"]
    )
    mock_data_Y12345 = build_random_record_store_data(
        "Y12345", ["20240601", "20240602", "20240603", "20240606"]
    )
    mock_record_store_data = mock_data_H81109 + mock_data_Y12345
    shuffle(mock_record_store_data)

    latest_record_in_H81109 = max(mock_data_H81109, key=lambda record: record.date)
    latest_record_in_Y12345 = max(mock_data_Y12345, key=lambda record: record.date)
    expected = (
        pl.DataFrame([latest_record_in_H81109, latest_record_in_Y12345])
        .drop("date", "statistic_id")
        .with_columns(CastDecimalToFloat)
    )

    actual = mock_service.summarise_record_store_data(mock_record_store_data)

    assert_frame_equal(actual, expected, check_row_order=False)


def test_summarise_organisation_data(mock_service):
    mock_data_H81109 = build_random_organisation_data(
        "H81109", ["20240603", "20240604", "20240605", "20240606", "20240607"]
    )
    mock_data_Y12345 = build_random_organisation_data(
        "Y12345", ["20240603", "20240604", "20240605", "20240606", "20240607"]
    )
    mock_input_data = {"H81109": mock_data_H81109, "Y12345": mock_data_Y12345}

    mock_organisation_data = mock_data_H81109 + mock_data_Y12345
    shuffle(mock_organisation_data)

    actual = mock_service.summarise_organisation_data(mock_organisation_data)

    for ods_code in mock_input_data.keys():
        mock_data_of_ods_code = mock_input_data[ods_code]
        row_in_actual_data = actual.filter(pl.col("ods_code") == ods_code)
        assert_weekly_counts_match_sum_of_daily_counts(
            mock_data_of_ods_code, row_in_actual_data
        )
        assert_average_record_per_patient_correct(
            mock_data_of_ods_code, row_in_actual_data
        )
        assert_number_of_patient_correct(mock_data_of_ods_code, row_in_actual_data)


def assert_weekly_counts_match_sum_of_daily_counts(mock_data, row_in_actual_data):
    for count_type in ["viewed", "downloaded", "stored", "deleted"]:
        expected_weekly_count = sum(
            getattr(data, f"daily_count_{count_type}") for data in mock_data
        )
        actual_weekly_count = row_in_actual_data.item(0, f"weekly_count_{count_type}")
        assert actual_weekly_count == expected_weekly_count


def assert_average_record_per_patient_correct(mock_data, row_in_actual_data):
    expected_average_patient_record = sum(
        data.average_records_per_patient for data in mock_data
    ) / len(mock_data)
    actual_average_patient_record = row_in_actual_data.item(
        0, "average_records_per_patient"
    )
    assert actual_average_patient_record == float(expected_average_patient_record)


def assert_number_of_patient_correct(mock_data, row_in_actual_data):
    most_recent_record_in_mock_data = max(mock_data, key=lambda data: data.date)
    expected_number_of_patients = most_recent_record_in_mock_data.number_of_patients
    actual_number_of_patient = row_in_actual_data.item(0, "number_of_patients")
    assert actual_number_of_patient == expected_number_of_patients


def test_summarise_application_data(mock_service):
    pass
