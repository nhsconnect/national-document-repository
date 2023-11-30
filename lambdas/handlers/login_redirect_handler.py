from enums.logging_app_interaction import LoggingAppInteraction
from oauthlib.oauth2 import WebApplicationClient
from services.login_redirect_service import LoginRedirectService
from services.ssm_service import SSMService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.request_context import request_context

logger = LoggingService(__name__)


@set_request_context_for_logging
@override_error_check
@ensure_environment_variables(names=["AUTH_DYNAMODB_NAME"])
def lambda_handler(event, context):
    login_redirect_service = LoginRedirectService()
    request_context.app_interaction = LoggingAppInteraction.LOGIN.value
    return login_redirect_service.prepare_redirect_response(
        WebApplicationClient, SSMService
    )
