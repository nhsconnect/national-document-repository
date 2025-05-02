import json
import os
from datetime import datetime
from typing import Optional

import requests
from pydantic import BaseModel
from services.base.dynamo_service import DynamoDBService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.set_audit_arg import set_request_context_for_logging

logger = LoggingService(__name__)


class AlarmEntry(BaseModel):
    alarm_name: str
    time_created: str
    history: list[str] = []
    last_updated: Optional[str]
    slack_timestamp: Optional[str]
    channel_id: str
    time_to_exist: Optional[str]


@set_request_context_for_logging
@ensure_environment_variables(
    names=[
        "APPCONFIG_APPLICATION",
        "APPCONFIG_CONFIGURATION",
        "WEBHOOK_URL",
        "CONFLUENCE_BASE_URL",
        "ALARM_HISTORY_DYNAMODB_NAME" "ALERTING_SLACK_CHANNEL_ID",
    ]
)
def lambda_handler(event, context):

    logger.info(f"Received event: {event}")
    alarm_notifications = event.get("Records", [])

    dynamo_service = DynamoDBService()
    table_name = os.environ["ALARM_HISTORY_DYNAMODB_NAME"]

    for sns_message in alarm_notifications:
        message = json.loads(sns_message["Sns"]["Message"])
        alarm_name = message["AlarmName"]
        message["AlarmDescription"]
        alarm_state = message["NewStateValue"]
        alarm_time = message["StateChangeTime"]

        alarm_entry = get_alarm_history(alarm_name, dynamo_service, table_name)

        if not alarm_entry:
            new_entry = AlarmEntry(
                alarm_name=alarm_name,
                time_created=alarm_time,
                channel_id=os.environ["ALERTING_SLACK_CHANNEL_ID"],
            )
            update_alarm_state_history(new_entry, alarm_state)
            create_alarm_entry(dynamo_service, table_name, new_entry)

        # Check alarm exists 🔴  🟢

        # new alarm post create record

        # two alarm states, "OK" and "ALARM"

        # table needs, alarm name, time created, time last update, state history, current state, message_id?

        # set a timeout, half hour.


def format_alarm_name(alarm_name: str) -> str:
    underscore_stripped_string = alarm_name.replace("_", " ")
    return underscore_stripped_string.title()


def format_time_string(date_string: str) -> str:
    # needs to have timezone correct in it!
    return datetime.strftime(datetime.fromisoformat(date_string), "%H:%M:%S %d-%m-%Y")


# This needs changing.
def create_action_url(base_url: str, alarm_name: str) -> str:
    formatted_alarm_name = format_alarm_name(alarm_name)
    trimmed_alarm_name = formatted_alarm_name.split(" ")[1:]
    url_extension = " ".join(trimmed_alarm_name).replace(" ", "%20")
    search_query = "#:~:text="

    return f"{base_url}{search_query}{url_extension}"


# history can be a string list, Dynamo does support them
def update_alarm_state_history(alarm_entry: AlarmEntry, current_state: str):

    if current_state == "ALARM":
        alarm_entry.history.append("\U0001F534")

    if current_state == "OK":
        alarm_entry.history.append("\U0001F7E2")


def get_alarm_history(
    alarm_name: str, dynamo_service: DynamoDBService, table_name: str
):
    dynamo_service.query_table_by_index(
        table_name=table_name,
        index_name="AlarmNameIndex",
        search_key="AlarmName",
        search_condition=alarm_name,
    )


def update_alarm_state(
    dynamo_service: DynamoDBService, table_name, alarm_name: str, updated_alarm
) -> str:

    logger.info(f"Updating alarm entry for: {alarm_name}")

    dynamo_service.update_item(
        table_name=table_name,
        key_pair={"AlarmName": alarm_name},
    )


def create_alarm_entry(
    dynamo_service: DynamoDBService, table_name: str, alarm_entry: AlarmEntry
):
    new_entry = alarm_entry.model_to_dict(
        by_alias=True,
        exclude_none=True,
    )

    logger.info(f"Creating new alarm entry for {alarm_entry.alarm_name}")

    dynamo_service.create_item(table_name=table_name, item=new_entry)


def update_new_entry_with_slack_message_id():
    pass


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
                                "text": format_alarm_name(alarm_entry.alarm_name),
                                "wrap": True,
                            },
                            {
                                "type": "TextBlock",
                                "text": alarm_entry.history,
                                "wrap": True,
                            },
                            {
                                "type": "TextBlock",
                                # look at how we are handling time entries on other models and tables.
                                "text": f"This state change happened at: {alarm_entry.time_created}",
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
