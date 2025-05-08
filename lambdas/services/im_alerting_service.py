import json
import os
from datetime import datetime, timedelta

import boto3
import requests
from enums.alarm_history_fields import AlarmHistoryFields
from models.alarm_entry import AlarmEntry
from services.base.dynamo_service import DynamoDBService
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class IMAlertingService:
    def __init__(self, message):
        self.dynamo_service = DynamoDBService()
        self.table_name = os.environ["ALARM_HISTORY_DYNAMODB_NAME"]
        self.alarm_severities = {
            "high": "\U0001F534",
            "medium": "\U0001F7E0",
            "low": "\U0001F7E1",
            "ok": "\U0001F7E2",
        }
        self.webhook_url = os.environ["WEBHOOK_URL"]
        self.confluence_base_url = os.environ["CONFLUENCE_BASE_URL"]
        self.message = message

    def handle_alarm_alert(self, message):

        alarm_name = message["AlarmName"]
        # alarm_description = message["AlarmDescription"]
        alarm_state = message["NewStateValue"]
        alarm_time = message["StateChangeTime"]

        alarm_entries = self.get_alarm_history(alarm_name)

        if not alarm_entries:
            logger.info(f"No alarm history for {alarm_name}")
            self.handle_new_alarm_episode(alarm_name, alarm_time, alarm_state)

        else:
            for alarm_entry in alarm_entries:
                if self.is_active_episode(alarm_entry):
                    self.handle_current_alarm_episode(
                        alarm_entry=alarm_entry,
                        alarm_name=alarm_name,
                        alarm_state=alarm_state,
                    )

                elif self.is_episode_expired(alarm_entry):
                    self.handle_new_alarm_episode(
                        alarm_name=alarm_name,
                        alarm_state=alarm_state,
                        alarm_time=alarm_time,
                    )

                elif alarm_entry.time_to_exist:
                    alarm_entry.time_to_exist = None
                    self.handle_current_alarm_episode(
                        alarm_entry=alarm_entry,
                        alarm_name=alarm_name,
                        alarm_state=alarm_state,
                    )

    def is_episode_expired(self, alarm_entry: AlarmEntry) -> bool:
        current_time = datetime.now().timestamp()

        return current_time >= alarm_entry.expires_at

    def is_active_episode(self, alarm_entry: AlarmEntry) -> bool:
        return False if alarm_entry.time_to_exist else True

    def handle_new_alarm_episode(
        self, alarm_name: str, alarm_time: str, alarm_state: str
    ):
        logger.info(f"Creating new alarm episode {alarm_name}:{alarm_time}")
        new_entry = AlarmEntry(
            alarm_name=self.format_alarm_name(alarm_name),
            time_created=self.create_alarm_timestamp(alarm_time),
            last_updated=self.create_alarm_timestamp(alarm_time),
            channel_id=os.environ["ALERTING_SLACK_CHANNEL_ID"],
        )
        AlarmEntry.model_validate(new_entry)
        self.update_alarm_state_history(new_entry, alarm_state, alarm_name)
        self.create_alarm_entry(new_entry)
        self.send_teams_alert(new_entry)

    def handle_current_alarm_episode(
        self, alarm_entry: AlarmEntry, alarm_state: str, alarm_name: str
    ):
        logger.info(
            f"Updating alarm episode {alarm_entry.alarm_name}:{alarm_entry.time_created}"
        )
        self.update_alarm_state_history(alarm_entry, alarm_state, alarm_name)
        self.update_alarm_state_history(alarm_entry)
        self.send_teams_alert(alarm_entry)

    def create_alarm_entry(self, alarm_entry: AlarmEntry):
        new_entry = alarm_entry.model_dump(
            by_alias=True,
            exclude_none=True,
        )

        logger.info(f"Creating new alarm entry for {alarm_entry.alarm_name}")

        self.dynamo_service.create_item(table_name=self.table_name, item=new_entry)

    def get_alarm_history(self, alarm_name: str):
        logger.info(
            f"Checking if {self.format_alarm_name(alarm_name)} already exists on alarm table"
        )
        results = self.dynamo_service.query_table_by_index(
            table_name=self.table_name,
            index_name="AlarmNameIndex",
            search_key="AlarmName",
            search_condition=self.format_alarm_name(alarm_name),
        )
        return (
            [AlarmEntry.model_validate(item) for item in results["Items"]]
            if results
            else []
        )

    def update_alarm_state_history(
        self, alarm_entry: AlarmEntry, current_state: str, alarm_name: str
    ):
        logger.info(f"Updating alarm state history for {alarm_entry.alarm_name}")
        if current_state == "ALARM":
            for key in self.alarm_severities.keys():
                if alarm_name.endswith(key):
                    alarm_entry.history.append(self.alarm_severities[key])

        if current_state == "OK" and self.all_alarm_state_ok(alarm_name):
            alarm_entry.history.append(self.alarm_severities["ok"])
            logger.info(
                f"All alarms for {alarm_entry.alarm_name} are in OK state, adding TTL."
            )
            self.add_ttl_to_alarm_entry(alarm_entry)

        alarm_entry.last_updated = int(datetime.now().timestamp())

    def update_alarm_table(
        self, dynamo_service: DynamoDBService, table_name, alarm_entry: AlarmEntry
    ) -> str:

        logger.info(f"Updating alarm table entry for: {alarm_entry.alarm_name}")

        fields_to_update = {
            AlarmHistoryFields.HISTORY: alarm_entry.history,
            AlarmHistoryFields.LASTUPDATED: int(datetime.now().timestamp()),
        }

        if alarm_entry.time_to_exist:
            fields_to_update[AlarmHistoryFields.TIMETOEXIST] = alarm_entry.time_to_exist

        dynamo_service.update_item(
            table_name=table_name,
            key_pair={
                AlarmHistoryFields.ALARMNAME: alarm_entry.alarm_name,
                AlarmHistoryFields.TIMECREATED: alarm_entry.time_created,
            },
            updated_fields=fields_to_update,
        )

    def all_alarm_state_ok(self, alarm_name) -> bool:
        alarm_prefix = alarm_name.rsplit("_", 1)[0]

        logger.info(f"Checking state for all alarms with prefix: {alarm_prefix}")

        client = boto3.client("cloudwatch")
        response = client.describe_alarms(
            AlarmNamePrefix=alarm_prefix,
        )

        alarm_states = [alarm["StateValue"] for alarm in response["MetricAlarms"]]

        return all(state == "OK" for state in alarm_states)

    def add_ttl_to_alarm_entry(self, alarm_entry: AlarmEntry):
        alarm_entry.time_to_exist = int(
            datetime.now() + timedelta(minutes=5).timestamp()
        )

    def create_alarm_timestamp(slef, alarm_time: str) -> int:
        return int(datetime.fromisoformat(alarm_time).timestamp())

    def format_time_string(self, time_stamp: int) -> str:
        return datetime.strftime(
            datetime.fromtimestamp(time_stamp), "%H:%M:%S %d-%m-%Y"
        )

    def format_alarm_name(self, alarm_name: str) -> str:
        underscore_stripped_string = alarm_name.replace("_", " ")
        return underscore_stripped_string.rsplit(" ", 1)[0].title()

    def unpack_alarm_history(self, alarm_history: list) -> str:
        history_string = ""
        for item in alarm_history:
            history_string += item + " "

        return history_string

    def create_action_url(self, base_url: str, alarm_name: str) -> str:
        url_extension = alarm_name.replace(" ", "%20")
        search_query = "#:~:text="

        return f"{base_url}{search_query}{url_extension}"

    def send_teams_alert(self, alarm_entry: AlarmEntry):
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
                                    "text": f"{alarm_entry.alarm_name} Alert",
                                    "wrap": True,
                                },
                                {
                                    "type": "TextBlock",
                                    "text": f"Alarm History: {self.unpack_alarm_history(alarm_entry.history)}",
                                    "wrap": True,
                                },
                                {
                                    "type": "TextBlock",
                                    # look at how we are handling time entries on other models and tables.
                                    "text": f"This state change happened at: {self.format_time_string(alarm_entry.last_updated)}",
                                    "wrap": True,
                                },
                            ],
                            "actions": [
                                {
                                    "type": "Action.OpenUrl",
                                    "title": "Find out what to do",
                                    "url": self.create_action_url(
                                        self.confluence_base_url, alarm_entry.alarm_name
                                    ),
                                },
                            ],
                        },
                    }
                ],
            }
        )

        headers = {"Content-Type": "application/json"}

        requests.request("POST", self.webhook_url, headers=headers, data=payload)
