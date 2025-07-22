import pytest
from enums.feature_flags import FeatureFlags
from services.dynamic_configuration_service import DynamicConfigurationService
from utils.request_context import request_context


@pytest.fixture
def configuration_service(mocker):
    mocker.patch("services.dynamic_configuration_service.FeatureFlagService")
    configuration_service = DynamicConfigurationService()
    yield configuration_service


def test_set_auth_ssm_prefix_to_password_when_flag_is_disabled(configuration_service):
    configuration_service.feature_flag_service.get_feature_flags_by_flag.return_value = {
        FeatureFlags.USE_SMARTCARD_AUTH.value: False
    }

    configuration_service.set_auth_ssm_prefix()

    assert request_context.auth_ssm_prefix == "/auth/password/"


def test_set_auth_ssm_prefix_to_smartcard_when_flag_is_enable(configuration_service):
    configuration_service.feature_flag_service.get_feature_flags_by_flag.return_value = {
        FeatureFlags.USE_SMARTCARD_AUTH.value: True
    }

    configuration_service.set_auth_ssm_prefix()

    assert request_context.auth_ssm_prefix == "/auth/smartcard/"
