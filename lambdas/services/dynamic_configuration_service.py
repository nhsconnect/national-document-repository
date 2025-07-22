from enums.feature_flags import FeatureFlags
from services.feature_flags_service import FeatureFlagService
from utils.audit_logging_setup import LoggingService
from utils.request_context import request_context

logger = LoggingService(__name__)


class DynamicConfigurationService:
    def __init__(self):
        self.feature_flag_service = FeatureFlagService()

    def set_auth_ssm_prefix(self) -> None:
        auth_flag_name = FeatureFlags.USE_SMARTCARD_AUTH.value
        use_smartcard_lambda_enabled_flag_object = (
            self.feature_flag_service.get_feature_flags_by_flag(auth_flag_name)
        )
        if use_smartcard_lambda_enabled_flag_object[auth_flag_name]:
            request_context.auth_ssm_prefix = "/auth/smartcard/"
        else:
            request_context.auth_ssm_prefix = "/auth/password/"
        logger.info("Setting auth ssm prefix to " + request_context.auth_ssm_prefix)
