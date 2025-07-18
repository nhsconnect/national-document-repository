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
        prefix = "/auth/smartcard/"

        try:
            auth_flag_name = FeatureFlags.MOCK_LOGIN_ENABLED.value
            flags = self.feature_flag_service.get_feature_flags_by_flag(auth_flag_name)
            if flags.get(auth_flag_name):
                prefix = "/auth/mock/"
        except FeatureFlagsException:
            pass

        logger.info(f"Setting auth ssm prefix to {prefix}")
        request_context.auth_ssm_prefix = prefix

    def is_auth_mocked(self) -> bool:
        return getattr(request_context, "auth_ssm_prefix", "") == "/auth/mock/"
