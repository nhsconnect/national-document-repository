import json
import logging

from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


@override_error_check
@handle_lambda_exceptions
def lambda_handler(event, context):
    logger.info(json.dumps(event))
    response = {
        "status": "302",  # Redirect status code
        "statusDescription": "Found",
        "headers": {
            "location": [{"key": "Location", "value": "https://www.google.co.uk"}],
            "hello": [{"key": "Hello", "value": "World"}],
        },
    }

    return response
