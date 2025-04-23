import json
import os

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
                                    "text": card_title,
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
                                    "text": f"This state change happened at {alarm_time}",
                                    "wrap": True,
                                },
                            ],
                        },
                    }
                ],
            }
        )

        headers = {"Content-Type": "application/json"}

        response = requests.request("POST", url, headers=headers, data=payload)
        logger.info(response.text)
