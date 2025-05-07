import json
import os
from datetime import datetime
from enum import StrEnum
from typing import Optional

import boto3
import requests
from pydantic import AliasGenerator, BaseModel, ConfigDict
from pydantic.alias_generators import to_pascal
from services.base.dynamo_service import DynamoDBService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.set_audit_arg import set_request_context_for_logging

logger = LoggingService(__name__)


alarm_severities = {
    "high": "\U0001F534",
    "medium": "\U0001F7E0",
    "low": "\U0001F7E1",
    "ok": "\U0001F7E2",
}


class AlarmEntry(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_pascal, serialization_alias=to_pascal
        )
    )
    alarm_name: str
    time_created: int
    history: list[str] = []
    last_updated: Optional[int] = None
    slack_timestamp: Optional[float] = None
    channel_id: str
    time_to_exist: Optional[int] = None


class AlarmHistoryFields(StrEnum):
    ALARMNAME = "AlarmName"
    TIMECREATED = "TimeCreated"
    LASTUPDATED = "LastUpdated"
    CHANNELID = "ChannelId"
    HISTORY = "History"
    SLACKTIMESTAMP = "SlackTimestamp"
    TIMETOEXIST = "TimeToExist"


@set_request_context_for_logging
@ensure_environment_variables(
    names=[
        "APPCONFIG_APPLICATION",
        "APPCONFIG_CONFIGURATION",
        "WEBHOOK_URL",
        "CONFLUENCE_BASE_URL",
        "ALARM_HISTORY_DYNAMODB_NAME",
        "ALERTING_SLACK_CHANNEL_ID",
    ]
)
def lambda_handler(event, context):

    logger.info(f"Received event: {event}")
    alarm_notifications = event.get("Records", [])

    dynamo_service = DynamoDBService()
    table_name = os.environ["ALARM_HISTORY_DYNAMODB_NAME"]

    for sns_message in alarm_notifications:
        message = json.loads(sns_message["Sns"]["Message"])
        logger.info(message)
        alarm_name = message["AlarmName"]
        message["AlarmDescription"]
        alarm_state = message["NewStateValue"]
        alarm_time = message["StateChangeTime"]

        alarm_entries = get_alarm_history(alarm_name, dynamo_service, table_name)

        if not alarm_entries:

            logger.info(f"No alarm entry found for {format_alarm_name(alarm_name)}")

            new_entry = AlarmEntry(
                alarm_name=format_alarm_name(alarm_name),
                time_created=create_alarm_timestamp(alarm_time),
                last_updated=create_alarm_timestamp(alarm_time),
                channel_id=os.environ["ALERTING_SLACK_CHANNEL_ID"],
            )
            AlarmEntry.model_validate(new_entry)
            update_alarm_state_history(new_entry, alarm_state, alarm_name)
            create_alarm_entry(dynamo_service, table_name, new_entry)

            send_teams_alert(new_entry)

        else:

            send_teams_alert(alarm_entries[0])


def create_alarm_timestamp(alarm_time: str) -> int:
    return int(datetime.fromisoformat(alarm_time).timestamp())


def get_current_timestamp() -> int:
    return int(datetime.now().timestamp())


def format_alarm_name(alarm_name: str) -> str:
    underscore_stripped_string = alarm_name.replace("_", " ")
    return underscore_stripped_string.rsplit(" ", 1)[0].title()


def format_time_string(time_stamp: int) -> str:
    # needs to have timezone correct in it!
    return datetime.strftime(datetime.fromtimestamp(time_stamp), "%H:%M:%S %d-%m-%Y")


# This needs changing.
def create_action_url(base_url: str, alarm_name: str) -> str:
    url_extension = " ".join(alarm_name).replace(" ", "%20")
    search_query = "#:~:text="

    return f"{base_url}{search_query}{url_extension}"


# history can be a string list, Dynamo does support them
def update_alarm_state_history(
    alarm_entry: AlarmEntry, current_state: str, alarm_name: str
):

    if current_state == "ALARM":
        for key in alarm_severities.keys():
            if alarm_name.endswith(key):
                alarm_entry.history.append(alarm_severities[key])

    if current_state == "OK" and all_alarm_state_ok(alarm_entry):
        alarm_entry.history.append(alarm_severities["ok"])

    alarm_entry.last_updated = get_current_timestamp()


def get_alarm_history(
    alarm_name: str, dynamo_service: DynamoDBService, table_name: str
):

    logger.info(
        f"Checking if {format_alarm_name(alarm_name)} already exists on alarm table"
    )
    results = dynamo_service.query_table_by_index(
        table_name=table_name,
        index_name="AlarmNameIndex",
        search_key="AlarmName",
        search_condition=format_alarm_name(alarm_name),
    )
    return (
        [AlarmEntry.model_validate(item) for item in results["Items"]]
        if results
        else []
    )


def update_alarm_table(
    dynamo_service: DynamoDBService, table_name, alarm_entry: AlarmEntry
) -> str:

    logger.info(f"Updating alarm table entry for: {alarm_entry.alarm_name}")

    dynamo_service.update_item(
        table_name=table_name,
        key_pair={
            AlarmHistoryFields.ALARMNAME: alarm_entry.alarm_name,
            AlarmHistoryFields.TIMECREATED: alarm_entry.time_created,
        },
        updated_fields={
            AlarmHistoryFields.HISTORY: alarm_entry.history,
            AlarmHistoryFields.LASTUPDATED: int(datetime.now().timestamp()),
        },
    )


def create_alarm_entry(
    dynamo_service: DynamoDBService, table_name: str, alarm_entry: AlarmEntry
):
    new_entry = alarm_entry.model_dump(
        by_alias=True,
        exclude_none=True,
    )

    logger.info(f"Creating new alarm entry for {alarm_entry.alarm_name}")

    dynamo_service.create_item(table_name=table_name, item=new_entry)


def update_new_entry_with_slack_message_id():
    pass


def unpack_alarm_history(alarm_history: list) -> str:
    history_string = ""
    for item in alarm_history:
        history_string += item + " "

    return history_string


def all_alarm_state_ok(alarm_name) -> bool:

    alarm_prefix = alarm_name.rsplit("_", 1)[0]

    logger.info(f"Checking state for all alarms with prefix: {alarm_prefix}")

    client = boto3.client("cloudwatch")
    response = client.describe_alarms(
        AlarmNamePrefix=alarm_prefix,
    )

    alarm_states = [alarm["StateValue"] for alarm in response["MetricAlarms"]]

    return all(state == "OK" for state in alarm_states)


def send_teams_alert(alarm_entry: AlarmEntry):

    webhook_url = os.environ["WEBHOOK_URL"]
    confluence_base_url = os.environ["CONFLUENCE_BASE_URL"]

    logger.info(f"Sending teams alert for: {alarm_entry.alarm_name}")

    payload = json.dumps(
        {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "contentUrl": None,
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.4",
                        "body": [
                            {
                                "type": "TextBlock",
                                "size": "Medium",
                                "weight": "Bolder",
                                "text": alarm_entry.alarm_name,
                                "wrap": True,
                            },
                            {
                                "type": "TextBlock",
                                "text": unpack_alarm_history(alarm_entry.history),
                                "wrap": True,
                            },
                            {
                                "type": "TextBlock",
                                # look at how we are handling time entries on other models and tables.
                                "text": f"This state change happened at: {format_time_string(alarm_entry.last_updated)}",
                                "wrap": True,
                            },
                        ],
                        "actions": [
                            {
                                "type": "Action.OpenUrl",
                                "title": "Find out what to do",
                                "url": create_action_url(
                                    confluence_base_url, alarm_entry.alarm_name
                                ),
                            },
                        ],
                    },
                }
            ],
        }
    )

    headers = {"Content-Type": "application/json"}

    requests.request("POST", webhook_url, headers=headers, data=payload)
