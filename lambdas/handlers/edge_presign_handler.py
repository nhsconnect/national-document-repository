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
    request = event["Records"][0]["cf"]["request"]
    logger.info(json.dumps(request))
    return request
