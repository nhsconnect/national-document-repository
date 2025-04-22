import json

import requests
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.set_audit_arg import set_request_context_for_logging

logger = LoggingService(__name__)


@set_request_context_for_logging
@ensure_environment_variables(
    names=[
        "APPCONFIG_APPLICATION",
        "APPCONFIG_CONFIGURATION",
    ]
)
def lambda_handler(event, context):

    url = "<HTTP POST URL>"

    alarm_notifications = event.get("Records", [])

    for sns_message in alarm_notifications:
        card_title = sns_message["Sns"]["Message"]["AlarmName"]
        card_description = sns_message["Sns"]["Message"]["AlarmDescription"]
        alarm_state = sns_message["Sns"]["Message"]["NewStateValue"]
        alarm_time = sns_message["Sns"]["Message"]["StateChangeTime "]

        colour = "red" if alarm_state == "ALARM" else "green"

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
                                    "size": "medium",
                                    "weight": "bold",
                                    "text": card_title,
                                    "color": colour,
                                },
                                {
                                    "type": "TextBlock",
                                    "text": card_description,
                                    "wrap": True,
                                },
                                {
                                    "type": "TextBlock",
                                    "text": f"This state change happened at {alarm_time}",
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
