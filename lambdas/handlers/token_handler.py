import json

from enums.feature_flags import FeatureFlags
from enums.lambda_error import LambdaError
from enums.logging_app_interaction import LoggingAppInteraction
from services.dynamic_configuration_service import DynamicConfigurationService
from services.feature_flags_service import FeatureFlagService
from services.login_service import LoginService
from services.mock_login_service import MockLoginService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.lambda_exceptions import LoginException
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = LoggingService(__name__)


@set_request_context_for_logging
@override_error_check
@ensure_environment_variables(
    names=["AUTH_STATE_TABLE_NAME", "AUTH_SESSION_TABLE_NAME", "MOCK_CIS2_API_KEY_SSM"]
)
@handle_lambda_exceptions
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.LOGIN.value
    logger.info("Token request handler triggered")

    configuration_service = DynamicConfigurationService()
    configuration_service.set_auth_ssm_prefix()

    login_service = _get_login_service()
    try:
        response = _generate_session(event, login_service)
        return ApiGatewayResponse(
            200, json.dumps(response), "GET"
        ).create_api_gateway_response()
    except Exception as exc:
        return _generate_error_response(exc, login_service)


def _get_login_service():
    """
    Decides whether to use the mock or the real CIS2 journey
    based on the feature flag.
    """
    flag_service = FeatureFlagService()
    feature_flag = flag_service.get_feature_flags_by_flag(
        FeatureFlags.MOCK_CIS2_LOGIN_ENABLED
    )
    return (
        MockLoginService()
        if feature_flag[FeatureFlags.MOCK_CIS2_LOGIN_ENABLED]
        else LoginService()
    )


def _generate_session(event: dict, service: LoginService):
    """
    Calls `generate_session` on the chosen service.

    * Mock service  -> username and password
    * Real service  -> code & state extracted from the CIS2 redirect
    """
    if isinstance(service, MockLoginService):
        username, password = _get_and_validate_query_params(event, service)
        return service.generate_session(username=username, password=password)

    auth_code, state = _get_and_validate_query_params(event, service)

    response = service.generate_session(state, auth_code)
    logger.audit_splunk_info(
        "User logged in successfully", {"Result": "Successful login"}
    )
    return response


def _get_and_validate_query_params(
    event: dict, service: LoginService
) -> tuple[str, str]:
    params = event.get("queryStringParameters") or {}

    if isinstance(service, MockLoginService):
        username, password = params.get("username"), params.get("password")
        if not (username and password):
            raise LoginException(400, LambdaError.LoginBadAuth)
        return username, password

    auth_code, state = params.get("code"), params.get("state")
    if not (auth_code and state):
        raise LoginException(400, LambdaError.LoginNoState)
    return auth_code, state


def _generate_error_response(exc: Exception, service):
    if isinstance(exc, (KeyError, TypeError)):
        logger.error(
            f"{LambdaError.LoginNoAuth.to_str()}: {str(exc)}",
            {"Result": "Unsuccessful login"},
        )
        return ApiGatewayResponse(
            400, LambdaError.LoginNoAuth.create_error_body(), "GET"
        ).create_api_gateway_response()

    if isinstance(exc, LoginException):
        if exc.error == LambdaError.LoginNoRole:
            allowed_roles = service.token_handler_ssm_service.get_smartcard_role_codes()
            error_body = LambdaError.LoginNoRole.create_error_body(roles=allowed_roles)
            return ApiGatewayResponse(
                401, error_body, "GET"
            ).create_api_gateway_response()
        return ApiGatewayResponse(
            exc.status_code, exc.error.create_error_body(), "GET"
        ).create_api_gateway_response()

    logger.error(
        f"{LambdaError.LoginNoAuth.to_str()}: {str(exc)}",
        {"Result": "Unsuccessful login"},
    )
    return ApiGatewayResponse(
        400, LambdaError.LoginNoAuth.create_error_body(), "GET"
    ).create_api_gateway_response()
