from enums.feature_flags import FeatureFlags
from services.feature_flags_service import FeatureFlagService
from utils.audit_logging_setup import LoggingService
from utils.lambda_exceptions import FeatureFlagsException
from utils.request_context import request_context

logger = LoggingService(__name__)


class DynamicConfigurationService:
    def __init__(self):
        self.feature_flag_service = FeatureFlagService()

    def set_auth_ssm_prefix(self) -> None:
        auth_flag_name = FeatureFlags.MOCK_LOGIN_ENABLED.value

        try:
            use_mock_login_enabled_flag_object = (
                self.feature_flag_service.get_feature_flags_by_flag(auth_flag_name)
            )
        except FeatureFlagsException:
            logger.info("Setting auth ssm prefix to smartcard login")
            request_context.auth_ssm_prefix = "/auth/smartcard/"
            return

        if use_mock_login_enabled_flag_object[auth_flag_name]:
            request_context.auth_ssm_prefix = "/auth/mock/"
        else:
            request_context.auth_ssm_prefix = "/auth/smartcard/"
        logger.info("Setting auth ssm prefix to " + request_context.auth_ssm_prefix)
