import json
import time

from services.base.nhs_oauth_service import NhsOauthService
from services.base.ssm_service import SSMService
from utils.audit_logging_setup import LoggingService
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.exceptions import OAuthErrorException

logger = LoggingService(__name__)


@set_request_context_for_logging
@override_error_check
@handle_lambda_exceptions
def lambda_handler(event, context):
    logger.info("Attempting to generate and store new NHS OAuth token via Lambda")

    ssm_service = SSMService()
    auth_service = NhsOauthService(ssm_service)

    max_retries = 5
    retry_delay_seconds = 10

    for attempt_count in range(1, max_retries + 1):
        try:
            access_token_response = auth_service.get_nhs_oauth_response()
            auth_service.update_access_token_ssm(json.dumps(access_token_response))
            return
        except OAuthErrorException as e:
            logger.warning(
                f"Failed to retrieve access token on attempt number: {attempt_count} - failed due to: {e}"
            )
            if attempt_count < max_retries:
                time.sleep(retry_delay_seconds)
            else:
                logger.error(
                    f"Failed to refresh the access token after {max_retries} attempts"
                )
                raise e
