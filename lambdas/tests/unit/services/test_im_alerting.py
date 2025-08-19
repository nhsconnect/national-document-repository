from copy import deepcopy
from datetime import datetime

import pytest
from enums.alarm_history_field import AlarmHistoryField
from enums.alarm_severity import AlarmSeverity
from freezegun.api import freeze_time
from models.alarm_entry import AlarmEntry
from services.im_alerting_service import IMAlertingService
from tests.unit.conftest import (
    MOCK_ALARM_HISTORY_TABLE,
    MOCK_ALERTING_SLACK_CHANNEL_ID,
    MOCK_CONFLUENCE_URL,
    MOCK_LG_METADATA_SQS_QUEUE,
)

ALERT_TIME = "2025-04-17T15:10:41.433+0000"
TTL_IN_SECONDS = 300

queue_alert_message = {
    "AlarmName": "dev_lg_bulk_main_oldest_message_alarm_6d",
    "AlarmDescription": f"Alarm when a message in queue dev-{MOCK_LG_METADATA_SQS_QUEUE} is older than 6 days.",
    "NewStateValue": "ALARM",
    "StateChangeTime": ALERT_TIME,
    "OldStateValue": "OK",
    "Trigger": {
        "MetricName": "ApproximateAgeOfOldestMessage",
        "Namespace": "AWS/SQS",
        "StatisticType": "Statistic",
        "Statistic": "Maximum",
        "Unit": None,
        "Dimensions": [
            {
                "QueueName": f"dev-{MOCK_LG_METADATA_SQS_QUEUE}",
            }
        ],
    },
}

queue_alert_tags = {
    "alarm_group": f"dev-{MOCK_LG_METADATA_SQS_QUEUE}",
    "alarm_metric": "ApproximateAgeOfOldestMessage",
    "severity": "high",
}


lambda_alert_message = {
    "AlarmName": "dev-alarm_search_patient_details_handler_error",
    "AlarmDescription": "Triggers when an error has occurred in dev_SearchPatientDetailsLambda.",
    "AlarmConfigurationUpdatedTimestamp": "2025-04-17T15:08:51.604+0000",
    "NewStateValue": "ALARM",
    "StateChangeTime": ALERT_TIME,
    "OldStateValue": "OK",
    "Trigger": {
        "MetricName": "Errors",
        "Namespace": "AWS/Lambda",
        "StatisticType": "Statistic",
        "Statistic": "SUM",
        "Unit": None,
        "Dimensions": [
            {
                "value": "dev_SearchPatientDetailsLambda",
                "name": "FunctionName",
            }
        ],
    },
}


@pytest.fixture
def alerting_service(mocker, set_env):
    service = IMAlertingService(queue_alert_message)
    mocker.patch.object(service, "dynamo_service")
    mocker.patch.object(service, "get_all_alarm_tags")
    mocker.patch.object(service, "get_alarm_history")
    mocker.patch.object(service, "send_teams_alert")
    mocker.patch.object(service, "send_initial_slack_alert")
    mocker.patch.object(service, "send_slack_response")
    mocker.patch.object(service, "update_original_slack_message")
    yield service

@pytest.fixture
def ok_alerting_service(mocker, set_env):
    ok_state_event = deepcopy(queue_alert_message)
    ok_state_event["NewStateValue"] = "OK"

    service = IMAlertingService(ok_state_event)
    mocker.patch.object(service, "dynamo_service")
    mocker.patch.object(service, "get_all_alarm_tags")
    mocker.patch.object(service, "get_alarm_history")
    mocker.patch.object(service, "send_teams_alert")
    mocker.patch.object(service, "send_initial_slack_alert")
    mocker.patch.object(service, "send_slack_response")
    mocker.patch.object(service, "update_original_slack_message")
    mocker.patch.object(service, "wait_for_alarm_stabilisation")
    mocker.patch.object(service, "is_last_updated")
    mocker.patch.object(service, "all_alarm_state_ok")
    yield service


BASE_URL = MOCK_CONFLUENCE_URL
ALERT_TIMESTAMP = int(datetime.fromisoformat(ALERT_TIME).timestamp())

ALARM_METRIC_NAME = (
    f'{queue_alert_message["Trigger"]["Dimensions"][0]["QueueName"]}'
    f' {queue_alert_message["Trigger"]["MetricName"]}'
)


MOCK_ALARM_HISTORY = [AlarmSeverity.LOW, AlarmSeverity.MEDIUM, AlarmSeverity.HIGH, AlarmSeverity.OK]


@freeze_time(ALERT_TIME)
def test_handle_new_alert_happy_path(alerting_service):
    alerting_service.get_all_alarm_tags.return_value = queue_alert_tags
    alerting_service.get_alarm_history.return_value = []

    alarm_entry = AlarmEntry(
        alarm_name_metric=ALARM_METRIC_NAME,
        time_created=ALERT_TIMESTAMP,
        last_updated=ALERT_TIMESTAMP,
        channel_id=MOCK_ALERTING_SLACK_CHANNEL_ID,
        history=[AlarmSeverity.HIGH],
    )

    alerting_service.handle_alarm_alert()
    alerting_service.dynamo_service.create_item.assert_called_with(
        table_name=MOCK_ALARM_HISTORY_TABLE, item=alarm_entry.to_dynamo()
    )
    alerting_service.send_teams_alert.assert_called_with(alarm_entry)
    alerting_service.send_initial_slack_alert.assert_called_with(alarm_entry)
    alerting_service.send_slack_response.assert_called_with(alarm_entry)


@freeze_time(ALERT_TIME)
def test_handle_existing_alarm_entry_happy_path(alerting_service):
    existing_alarm_entry = AlarmEntry(
        alarm_name_metric=ALARM_METRIC_NAME,
        time_created=ALERT_TIMESTAMP,
        last_updated=ALERT_TIMESTAMP,
        channel_id=MOCK_ALERTING_SLACK_CHANNEL_ID,
        history=[AlarmSeverity.MEDIUM],
    )
    alerting_service.get_alarm_history.return_value = [existing_alarm_entry]
    alerting_service.get_all_alarm_tags.return_value = queue_alert_tags

    updated_alarm_entry = AlarmEntry(
        alarm_name_metric=ALARM_METRIC_NAME,
        time_created=ALERT_TIMESTAMP,
        last_updated=ALERT_TIMESTAMP,
        channel_id=MOCK_ALERTING_SLACK_CHANNEL_ID,
        history=[AlarmSeverity.MEDIUM, AlarmSeverity.HIGH],
    )

    updated_fields = {
        AlarmHistoryField.HISTORY: updated_alarm_entry.get_alarm_severity_list_as_string(),
        AlarmHistoryField.LASTUPDATED: ALERT_TIMESTAMP,
        AlarmHistoryField.SLACKTIMESTAMP: updated_alarm_entry.slack_timestamp,
        AlarmHistoryField.TIMETOEXIST: updated_alarm_entry.time_to_exist,
    }

    alerting_service.handle_alarm_alert()
    alerting_service.send_teams_alert.assert_called_with(updated_alarm_entry)
    alerting_service.send_slack_response.assert_called_with(updated_alarm_entry)
    alerting_service.update_original_slack_message.assert_called_with(
        updated_alarm_entry
    )

    alerting_service.dynamo_service.update_item.assert_called_with(
        table_name=MOCK_ALARM_HISTORY_TABLE,
        key_pair={
            AlarmHistoryField.ALARMNAMEMETRIC: updated_alarm_entry.alarm_name_metric,
            AlarmHistoryField.TIMECREATED: updated_alarm_entry.time_created,
        },
        updated_fields=updated_fields,
    )

@freeze_time(ALERT_TIME)
def test_handle_ok_action_happy_path(ok_alerting_service):
    ok_alerting_service.all_alarm_state_ok.return_value = True
    ok_alerting_service.is_last_updated.return_value = True
    ok_alerting_service.get_all_alarm_tags.return_value = queue_alert_tags
    existing_alarm_entry = AlarmEntry(
        alarm_name_metric=ALARM_METRIC_NAME,
        time_created=ALERT_TIMESTAMP,
        last_updated=ALERT_TIMESTAMP,
        channel_id=MOCK_ALERTING_SLACK_CHANNEL_ID,
        history=[AlarmSeverity.MEDIUM],
    )
    ok_alerting_service.get_alarm_history.return_value = [existing_alarm_entry]

    updated_alarm_entry = AlarmEntry(
        alarm_name_metric=ALARM_METRIC_NAME,
        time_created=ALERT_TIMESTAMP,
        last_updated=ALERT_TIMESTAMP,
        channel_id=MOCK_ALERTING_SLACK_CHANNEL_ID,
        history=[AlarmSeverity.MEDIUM, AlarmSeverity.OK],
        time_to_exist=ALERT_TIMESTAMP + TTL_IN_SECONDS,
    )

    updated_fields = {
        AlarmHistoryField.HISTORY: updated_alarm_entry.get_alarm_severity_list_as_string(),
        AlarmHistoryField.LASTUPDATED: ALERT_TIMESTAMP,
        AlarmHistoryField.SLACKTIMESTAMP: updated_alarm_entry.slack_timestamp,
        AlarmHistoryField.TIMETOEXIST: updated_alarm_entry.time_to_exist,
    }

    ok_alerting_service.handle_alarm_alert()

    ok_alerting_service.wait_for_alarm_stabilisation.assert_called()
    ok_alerting_service.is_last_updated.assert_called()
    ok_alerting_service.send_teams_alert.assert_called_with(updated_alarm_entry)
    ok_alerting_service.send_slack_response.assert_called_with(updated_alarm_entry)
    ok_alerting_service.update_original_slack_message.assert_called_with(
        updated_alarm_entry
    )

    ok_alerting_service.dynamo_service.update_item.assert_called_with(
        table_name=MOCK_ALARM_HISTORY_TABLE,
        key_pair={
            AlarmHistoryField.ALARMNAMEMETRIC: updated_alarm_entry.alarm_name_metric,
            AlarmHistoryField.TIMECREATED: updated_alarm_entry.time_created,
        },
        updated_fields=updated_fields,
    )

@freeze_time(ALERT_TIME)
def test_handle_ok_action_not_all_alarms_ok(mocker, ok_alerting_service):
    ok_alerting_service.all_alarm_state_ok.return_value = False
    ok_alerting_service.is_last_updated.return_value = True
    ok_alerting_service.get_all_alarm_tags.return_value = queue_alert_tags
    mocker.patch.object(ok_alerting_service, "add_ttl_to_alarm_entry")
    existing_alarm_entry = AlarmEntry(
        alarm_name_metric=ALARM_METRIC_NAME,
        time_created=ALERT_TIMESTAMP,
        last_updated=ALERT_TIMESTAMP,
        channel_id=MOCK_ALERTING_SLACK_CHANNEL_ID,
        history=[AlarmSeverity.MEDIUM],
    )
    ok_alerting_service.get_alarm_history.return_value = [existing_alarm_entry]


    ok_alerting_service.handle_alarm_alert()

    ok_alerting_service.wait_for_alarm_stabilisation.assert_not_called()
    ok_alerting_service.is_last_updated.assert_not_called()
    ok_alerting_service.add_ttl_to_alarm_entry.assert_not_called()
    ok_alerting_service.send_teams_alert.assert_not_called()
    ok_alerting_service.send_slack_response.assert_not_called()
    ok_alerting_service.update_original_slack_message.assert_not_called()
    ok_alerting_service.dynamo_service.update_item.assert_not_called()


@freeze_time(ALERT_TIME)
def test_handle_ok_action_not_last_updated(mocker, ok_alerting_service):
    ok_alerting_service.all_alarm_state_ok.return_value = True
    ok_alerting_service.is_last_updated.return_value = False
    ok_alerting_service.get_all_alarm_tags.return_value = queue_alert_tags
    mocker.patch.object(ok_alerting_service, "add_ttl_to_alarm_entry")

    existing_alarm_entry = AlarmEntry(
        alarm_name_metric=ALARM_METRIC_NAME,
        time_created=ALERT_TIMESTAMP,
        last_updated=ALERT_TIMESTAMP,
        channel_id=MOCK_ALERTING_SLACK_CHANNEL_ID,
        history=[AlarmSeverity.MEDIUM],
    )
    ok_alerting_service.get_alarm_history.return_value = [existing_alarm_entry]

    ok_alerting_service.handle_alarm_alert()

    ok_alerting_service.wait_for_alarm_stabilisation.assert_called()
    ok_alerting_service.is_last_updated.assert_called()
    ok_alerting_service.add_ttl_to_alarm_entry.assert_not_called()
    ok_alerting_service.send_teams_alert.assert_not_called()
    ok_alerting_service.send_slack_response.assert_not_called()
    ok_alerting_service.update_original_slack_message.assert_not_called()
    ok_alerting_service.dynamo_service.update_item.assert_not_called()


def test_is_last_updated():
    pass


def test_create_action_url_with_lambda_alert(alerting_service):
    expected = (
        "https://confluence.example.com#:~:text=SearchPatientDetailsLambda%20Errors"
    )
    alarm_metric_name = (
        f'{lambda_alert_message["Trigger"]["Dimensions"][0]["value"]}'
        f' {lambda_alert_message["Trigger"]["MetricName"]}'
    )

    actual = alerting_service.create_action_url(BASE_URL, alarm_metric_name)

    assert actual == expected


def test_create_action_url_with_queue_alert(alerting_service):

    expected = "https://confluence.example.com#:~:text=test%20bulk%20upload%20metadata%20queue%20ApproximateAgeOfOldestMessage"
    alarm_metric_name = (
        f'{queue_alert_message["Trigger"]["Dimensions"][0]["QueueName"]}'
        f' {queue_alert_message["Trigger"]["MetricName"]}'
    )

    actual = alerting_service.create_action_url(BASE_URL, alarm_metric_name)
    assert actual == expected


def test_create_alarm_timestamp(alerting_service):
    expected = ALERT_TIMESTAMP
    actual = alerting_service.create_alarm_timestamp(
        queue_alert_message["StateChangeTime"]
    )

    assert actual == expected


def test_unpacking_state_history_emoji_name(alerting_service):
    expected = ":large_yellow_circle: :large_orange_circle: :red_circle: :large_green_circle:"
    actual = alerting_service.unpack_alarm_history_emoji_name(MOCK_ALARM_HISTORY)
    assert actual == expected


def test_unpacking_state_history_unicode(alerting_service):
    expected = "\U0001F7E1 \U0001F7E0 \U0001F534 \U0001F7E2"
    actual = alerting_service.unpack_alarm_history_unicode(MOCK_ALARM_HISTORY)

    assert actual == expected


def test_compose_teams_message():
    pass


def test_compose_slack_message_blocks():
    pass


def test_format_time_string(alerting_service):
    expected = "15:10:41 17-04-2025 UTC"
    actual = alerting_service.format_time_string(ALERT_TIMESTAMP)

    assert actual == expected


def test_build_tags_filter(alerting_service):
    expected = [
        {"Key": "alarm_group", "Values": [f"dev-{MOCK_LG_METADATA_SQS_QUEUE}"]},
        {"Key": "alarm_metric", "Values": ["ApproximateAgeOfOldestMessage"]},
    ]

    actual = alerting_service.build_tag_filter(queue_alert_tags)
    assert actual == expected


@freeze_time(ALERT_TIME)
def test_add_ttl_to_alarm_entry(alerting_service):

    alarm_entry = AlarmEntry(
        alarm_name_metric=ALARM_METRIC_NAME,
        time_created=ALERT_TIMESTAMP,
        last_updated=ALERT_TIMESTAMP,
        channel_id=MOCK_ALERTING_SLACK_CHANNEL_ID,
        history=[AlarmSeverity.HIGH],
    )

    alerting_service.add_ttl_to_alarm_entry(alarm_entry)

    assert alarm_entry.time_to_exist == ALERT_TIMESTAMP + TTL_IN_SECONDS
