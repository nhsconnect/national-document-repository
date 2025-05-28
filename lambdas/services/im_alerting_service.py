import json
import os
import re
from datetime import datetime, timedelta
from time import sleep

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
        self.slack_emojis = {
            self.alarm_severities["high"]: "red_circle",
            self.alarm_severities["medium"]: "large_orange_circle",
            self.alarm_severities["low"]: "large_yellow_circle",
            self.alarm_severities["ok"]: "large_green_circle",
        }
        self.webhook_url = os.environ["TEAMS_WEBHOOK_URL"]
        self.confluence_base_url = os.environ["CONFLUENCE_BASE_URL"]
        self.message = message
        self.slack_headers = {
            "Authorization": "Bearer " + os.environ["SLACK_BOT_TOKEN"],
            "Content-type": "application/json; charset=utf-8",
        }

    def handle_alarm_alert(self):

        # alarm_name = self.message["AlarmName"] we don't care about the name any more, use the arn to get the tags
        alarm_state = self.message["NewStateValue"]
        alarm_time = self.message["StateChangeTime"]

        alarm_tags = self.get_all_alarm_tags()
        alarm_name = alarm_tags["alarm_group"] + " " + alarm_tags["metric"]

        alarm_entries = self.get_alarm_history(alarm_name)

        if not alarm_entries and alarm_state == "OK":
            logger.info(
                f"Alarm {alarm_name} is in OK state and no entries found for {alarm_name}"
            )
            return

        if not alarm_entries and alarm_state == "ALARM":
            logger.info(f"No current alarm history for {alarm_name}")
            self.handle_new_alarm_episode(
                alarm_name=alarm_name, alarm_time=alarm_time, tags=alarm_tags
            )

        else:
            all_alarms_expired = all(
                self.is_episode_expired(alarm_entry) for alarm_entry in alarm_entries
            )
            if all_alarms_expired:
                logger.info(
                    f"All alarm entries for {alarm_name} have expired, creating a new one"
                )
                self.handle_new_alarm_episode(
                    alarm_name=alarm_name,
                    alarm_time=alarm_time,
                    tags=alarm_tags,
                )
            else:
                for alarm_entry in alarm_entries:
                    if not self.is_episode_expired(alarm_entry):
                        self.handle_current_alarm_episode(
                            alarm_entry=alarm_entry,
                            alarm_state=alarm_state,
                            tags=alarm_tags,
                        )

    def is_episode_expired(self, alarm_entry: AlarmEntry) -> bool:
        if alarm_entry.time_to_exist:
            current_time = datetime.now().timestamp()
            return current_time >= alarm_entry.time_to_exist
        else:
            return False

    def handle_new_alarm_episode(self, alarm_name: str, alarm_time: str, tags: dict):
        logger.info(
            f"Creating new alarm episode {alarm_name}:{self.create_alarm_timestamp(alarm_time)}"
        )
        new_entry = AlarmEntry(
            alarm_name=alarm_name,
            time_created=self.create_alarm_timestamp(alarm_time),
            last_updated=self.create_alarm_timestamp(alarm_time),
            channel_id=os.environ["ALERTING_SLACK_CHANNEL_ID"],
        )
        AlarmEntry.model_validate(new_entry)
        self.update_alarm_state_history(new_entry, tags)
        self.send_teams_alert(new_entry)
        self.send_initial_slack_alert(new_entry)
        self.create_alarm_entry(new_entry)

    #     feels like alarm entry should be done first so that it exists in dynamo before send message
    # means adding in extra update when the slack response comes in so the correct object has the slack thread_ts needed

    def handle_current_alarm_episode(
        self, alarm_entry: AlarmEntry, alarm_state: str, tags: dict
    ):
        logger.info(
            f"Updating alarm episode {alarm_entry.alarm_name}:{alarm_entry.time_created}"
        )
        if alarm_state == "ALARM":
            logger.info(f"Handling Alarm action for {alarm_entry.alarm_name}")

            self.update_alarm_state_history(tags=tags, alarm_entry=alarm_entry)
            self.send_teams_alert(alarm_entry)
            self.send_slack_response(alarm_entry)
            self.update_original_slack_message(alarm_entry)
            self.update_alarm_table(alarm_entry)

        if alarm_state == "OK":
            self.handle_ok_action_trigger(tags=tags, alarm_entry=alarm_entry)

    def create_alarm_entry(self, alarm_entry: AlarmEntry):
        new_entry = alarm_entry.model_dump(
            by_alias=True,
            exclude_none=True,
        )
        logger.info(f"Creating new alarm entry for {alarm_entry.alarm_name}")
        self.dynamo_service.create_item(table_name=self.table_name, item=new_entry)

    def handle_ok_action_trigger(self, tags: dict, alarm_entry: AlarmEntry):
        logger.info(f"Handling OK action trigger for {alarm_entry.alarm_name}")

        if self.all_alarm_state_ok(tags):
            logger.info("Waiting for other alarms to be triggered before setting TTL.")
            sleep(180)
            if self.is_last_updated(alarm_entry):
                logger.info(
                    f"All alarms for {alarm_entry.alarm_name} are in OK state, adding TTL."
                )
                alarm_entry.history.append(self.alarm_severities["ok"])
                alarm_entry.last_updated = int(datetime.now().timestamp())
                self.add_ttl_to_alarm_entry(alarm_entry)
                self.update_alarm_table(alarm_entry)
                self.send_teams_alert(alarm_entry)
                self.send_slack_response(alarm_entry)
                self.update_original_slack_message(alarm_entry)

            else:
                logger.info("Alarm entry has been updated since reaching OK state")
                return

    def update_alarm_state_history(self, alarm_entry: AlarmEntry, tags: dict):

        for key in self.alarm_severities.keys():
            if tags.get("severity", None) == key:
                alarm_entry.history.append(self.alarm_severities[key])
        alarm_entry.time_to_exist = None
        alarm_entry.last_updated = int(datetime.now().timestamp())

    def get_alarm_history(self, alarm_name: str):
        logger.info(f"Checking if {alarm_name} already exists on alarm table")

        results = self.dynamo_service.query_table_by_index(
            table_name=self.table_name,
            index_name="AlarmNameIndex",
            search_key="AlarmName",
            search_condition=alarm_name,
        )

        return (
            [AlarmEntry.model_validate(item) for item in results["Items"]]
            if results
            else []
        )

    def is_last_updated(self, alarm_entry: AlarmEntry) -> bool:
        response = self.dynamo_service.get_item(
            table_name=self.table_name,
            key={
                AlarmHistoryFields.ALARMNAME: alarm_entry.alarm_name,
                AlarmHistoryFields.TIMECREATED: alarm_entry.time_created,
            },
        )
        entry_to_compare = AlarmEntry.model_validate(response["Item"])

        if alarm_entry.last_updated >= entry_to_compare.last_updated:
            logger.info(
                f"No other alarm has been triggered since {alarm_entry.alarm_name}:{alarm_entry.time_created} was last updated"
            )
            return True
        else:
            logger.info(
                f"Another alarm for {alarm_entry.alarm_name}:{alarm_entry.time_created} has been triggered since last updated"
            )
            return False

    def update_alarm_table(self, alarm_entry: AlarmEntry) -> str:

        logger.info(f"Updating alarm table entry for: {alarm_entry.alarm_name}")

        fields_to_update = {
            AlarmHistoryFields.HISTORY: alarm_entry.history,
            AlarmHistoryFields.LASTUPDATED: int(datetime.now().timestamp()),
            AlarmHistoryFields.TIMETOEXIST: alarm_entry.time_to_exist,
        }

        self.dynamo_service.update_item(
            table_name=self.table_name,
            key_pair={
                AlarmHistoryFields.ALARMNAME: alarm_entry.alarm_name,
                AlarmHistoryFields.TIMECREATED: alarm_entry.time_created,
            },
            updated_fields=fields_to_update,
        )

    def all_alarm_state_ok(self, tags: dict) -> bool:

        tag_filter = self.build_tag_filter(tags)
        client = boto3.client("resourcegroupstaggingapi")
        response = client.get_resources(
            ResourceTypeFilters=["cloudwatch:alarm"], TagFilters=tag_filter
        )

        resources = response["ResourceTagMappingList"]
        arns = []
        for resource in resources:
            arns.append(resource["ResourceARN"])

        alarm_names = self.extract_alarm_names_from_arns(arns)

        cloudwatch_client = boto3.client("cloudwatch")
        cloudwatch_response = cloudwatch_client.describe_alarms(
            AlarmNames=alarm_names,
        )

        alarm_states = [
            alarm["StateValue"] for alarm in cloudwatch_response["MetricAlarms"]
        ]

        return all(state == "OK" for state in alarm_states)

    def get_all_alarm_tags(self) -> dict:
        client = boto3.client("cloudwatch")
        response = client.list_tags_for_resource(ResourceARN=self.message["AlarmArn"])

        tags = {}
        if response["Tags"]:

            for tag in response["Tags"]:
                for key, value in tag.items():
                    tags[key] = tag[value]
        return tags

    def build_tag_filter(self, tags: dict) -> list:
        tag_filter = []

        for key, value in tags.items():
            if key == "alarm_group" or key == "metric":
                tag_filter.append({"Key": key, "Value": [value]})

        return tag_filter

    def extract_alarm_names_from_arns(self, arn_list: list) -> list:
        alarm_names = []
        for arn in arn_list:
            match = re.search(r"alarm:([^:]+)$", arn)
            if match:
                alarm_names.append(match.group(1))
            else:
                raise ValueError(f"Invalid alarm ARN format: {arn}")
        return alarm_names

    def add_ttl_to_alarm_entry(self, alarm_entry: AlarmEntry):
        alarm_entry.time_to_exist = int(
            (datetime.now() + timedelta(minutes=5)).timestamp()
        )

    def create_alarm_timestamp(self, alarm_time: str) -> int:
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
                                    "text": f"{alarm_entry.alarm_name} Alert: {alarm_entry.history[-1]}",
                                    "wrap": True,
                                },
                                {
                                    "type": "TextBlock",
                                    "text": f"Entry: {alarm_entry.alarm_name}:{alarm_entry.time_created}",
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

    def send_initial_slack_alert(self, alarm_entry: AlarmEntry):
        logger.info(
            f"Sending initial slack alert for: {alarm_entry.alarm_name}:{alarm_entry.time_created}"
        )
        slack_message = {}
        slack_message["channel"] = alarm_entry.channel_id
        slack_message["blocks"] = self.compose_slack_message(alarm_entry)

        slack_post_chat_api = "https://slack.com/api/chat.postMessage"
        response = requests.request(
            "POST",
            slack_post_chat_api,
            data=json.dumps(slack_message),
            headers=self.slack_headers,
        )
        logger.info(f"Slack response: {response.text}")
        response_json = json.loads(response.content)
        slack_timestamp = response_json["ts"]
        alarm_entry.slack_timestamp = slack_timestamp

        self.change_reaction(alarm_entry, "add")

    def send_slack_response(self, alarm_entry: AlarmEntry):
        logger.info(
            f"Sending slack thread response for: {alarm_entry.alarm_name}:{alarm_entry.time_created}"
        )
        slack_message = {}
        slack_message["channel"] = alarm_entry.channel_id
        slack_message["thread_ts"] = alarm_entry.slack_timestamp
        slack_message["blocks"] = self.compose_slack_message(alarm_entry)

        slack_post_chat_api = "https://slack.com/api/chat.postMessage"
        requests.request(
            "POST",
            slack_post_chat_api,
            data=json.dumps(slack_message),
            headers=self.slack_headers,
        )
        self.change_reaction(alarm_entry, "remove")
        self.change_reaction(alarm_entry, "add")

    def change_reaction(self, alarm_entry: AlarmEntry, action: str):
        logger.info(
            f"Changing slack reaction for alarm: {alarm_entry.alarm_name}:{alarm_entry.time_created}"
        )
        change_message = {}
        emoji = (
            self.slack_emojis.get(alarm_entry.history[-2])
            if action == "remove"
            else self.slack_emojis.get(alarm_entry.history[-1])
        )
        change_message["name"] = emoji
        change_message["channel"] = alarm_entry.channel_id
        change_message["timestamp"] = alarm_entry.slack_timestamp
        changeResponse = requests.post(
            "https://slack.com/api/reactions." + action,
            json=change_message,
            headers=self.slack_headers,
        )
        logger.info(
            action + " " + emoji + " reaction response: " + str(changeResponse.content)
        )

    def update_original_slack_message(self, alarm_entry: AlarmEntry):
        slack_message = {}
        slack_message["channel"] = alarm_entry.channel_id
        slack_message["ts"] = alarm_entry.slack_timestamp
        slack_message["blocks"] = self.compose_slack_message(alarm_entry)

        headers = {
            "Authorization": "Bearer " + self.slack_bot_token,
            "Content-type": "application/json; charset=utf-8",
        }

        slack_update_chat_api = "https://slack.com/api/chat.update"
        requests.request(
            "POST",
            slack_update_chat_api,
            data=json.dumps(slack_message),
            headers=headers,
        )

    def compose_slack_message(self, alarm_entry: AlarmEntry):
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{alarm_entry.alarm_name} Alert: {alarm_entry.history[-1]}",
                },
            },
            {
                "type": "divider",
            },
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": f"Alarm History: {self.unpack_alarm_history(alarm_entry.history)}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": f"This state change happened at: {self.format_time_string(alarm_entry.last_updated)}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*What to do:*\n <{self.create_action_url(self.confluence_base_url, alarm_entry.alarm_name)}>",
                },
            },
            # {
            #     "type": "image",
            #     "image_url": "https://singlecolorimage.com/get/"
            #     + alarm_entry.history[-1]
            #     + "/1x1",
            #     "alt_text": f"{self.slack_emojis.get(alarm_entry.history[-1])}",
            # },
        ]
        return blocks
