from datetime import datetime
from unittest import mock

from freezegun import freeze_time

from handlers.bulk_upload_report_handler import get_times_for_scan, write_items_to_csv


@freeze_time("2012-01-14 7:20:01")
def test_get_time_for_scan_after_7am():
    expected_end_report_time = datetime(2012, 1, 14, 7, 0, 0, 0)
    expected_start_report_time = datetime(2012, 1, 13, 7, 0, 0, 0)

    actual_start_time, actual_end_time = get_times_for_scan()

    assert expected_start_report_time == actual_start_time
    assert expected_end_report_time == actual_end_time

@freeze_time("2012-01-14 6:59:59")
def test_get_time_for_scan_before_7am():
    expected_end_report_time = datetime(2012, 1, 13, 7, 0, 0, 0)
    expected_start_report_time = datetime(2012, 1, 12, 7, 0, 0, 0)

    actual_start_time, actual_end_time = get_times_for_scan()

    assert expected_start_report_time == actual_start_time
    assert expected_end_report_time == actual_end_time

@freeze_time("2012-01-14 7:00:00")
def test_get_time_for_scan_at_7am():
    expected_end_report_time = datetime(2012, 1, 14, 7, 0, 0, 0)
    expected_start_report_time = datetime(2012, 1, 13, 7, 0, 0, 0)

    actual_start_time, actual_end_time = get_times_for_scan()

    assert expected_start_report_time == actual_start_time
    assert expected_end_report_time == actual_end_time
#
# def test_write_items_to_csv(mocker):
#     items = [{'id': 1, 'key': 'value'}, {'id': 2, 'key': 'value'}]
#
#     mock_open = mocker.patch("builtins.open", mock.mock_open())
#     mock_csv_object = mocker.patch('csv.DictWriter')
#
#     write_items_to_csv(items, 'path')
#     mock_open.assert_called_with('path', 'w')
#     mock_csv_object.assert_called_with(mock_open(), fieldnames=items[0].keys())
#     mock_csv_object.writeheader.assert_called_once()
#     mock_csv_object.writerow.assert_called_with(items[0])
#     mock_csv_object.writerow.assert_called_with(items[1])
#
