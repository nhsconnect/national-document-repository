import json
import os
from datetime import datetime

import requests
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.set_audit_arg import set_request_context_for_logging

logger = LoggingService(__name__)


@set_request_context_for_logging
@ensure_environment_variables(
    names=["APPCONFIG_APPLICATION", "APPCONFIG_CONFIGURATION", "WEBHOOK_URL"]
)
def lambda_handler(event, context):

    url = os.environ["WEBHOOK_URL"]

    logger.info(f"Received event: {event}")
    alarm_notifications = event.get("Records", [])

    for sns_message in alarm_notifications:
        message = json.loads(sns_message["Sns"]["Message"])
        card_title = message["AlarmName"]
        card_description = message["AlarmDescription"]
        alarm_state = message["NewStateValue"]
        alarm_time = message["StateChangeTime"]

        colour = "Warning" if alarm_state == "ALARM" else "Good"

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
                            "version": "1.2",
                            "body": [
                                {
                                    "type": "TextBlock",
                                    "size": "Medium",
                                    "weight": "Bolder",
                                    "text": format_alarm_name(card_title),
                                    "color": colour,
                                    "wrap": True,
                                },
                                {
                                    "type": "TextBlock",
                                    "text": card_description,
                                    "wrap": True,
                                },
                                {
                                    "type": "TextBlock",
                                    "text": f"This state change happened at: {format_time_string(alarm_time)}",
                                    "wrap": True,
                                },
                            ],
                            "actions": [
                                {
                                    "type": "Actions.OpenUrl",
                                    "title": "Find out what to do",
                                    "url": "",
                                }
                            ],
                        },
                    }
                ],
            }
        )

        headers = {"Content-Type": "application/json"}

        response = requests("POST", url, headers=headers, data=payload)
        logger.info(response.url)


def format_alarm_name(alarm_name: str) -> str:
    underscore_stripped_string = alarm_name.replace("_", " ")
    words = underscore_stripped_string.split(" ")
    capitalised_words = [word.capitalize() for word in words]
    return " ".join(capitalised_words)


def format_time_string(date_string: str) -> str:
    # needs to have timezone correct in it!
    return datetime.strftime(datetime.fromisoformat(date_string), "%H:%M:%S %d-%m-%Y")
