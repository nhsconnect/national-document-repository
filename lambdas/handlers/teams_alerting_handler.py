import json

import requests
from utils.audit_logging_setup import LoggingService
from utils.decorators import handle_lambda_exceptions
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.set_audit_arg import set_request_context_for_logging

logger = LoggingService(__name__)


@handle_lambda_exceptions
@set_request_context_for_logging
@ensure_environment_variables(
    names=[
        "APPCONFIG_APPLICATION",
        "APPCONFIG_CONFIGURATION",
    ]
)
def lambda_handler(event, context):

    logger.info(f"Received event: {json.dumps(event)}")

    url = "<HTTP POST URL>"

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
                                "text": "For Samples and Templates, see [https://adaptivecards.io/samples](https://adaptivecards.io/samples)",
                            }
                        ],
                    },
                }
            ],
        }
    )
    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)
    logger.info(response.text)
