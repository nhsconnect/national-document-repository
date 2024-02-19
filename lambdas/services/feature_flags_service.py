import os

import requests
from enums.lambda_error import LambdaError
from requests.exceptions import JSONDecodeError
from utils.audit_logging_setup import LoggingService
from utils.lambda_exceptions import FeatureFlagsException

logger = LoggingService(__name__)


class FeatureFlagService:
    def __init__(self):
        app_config_port = 2772
        self.app_config_url = (
            f"http://localhost:{app_config_port}"
            + f'/applications/{os.environ["APPCONFIG_APPLICATION"]}'
            + f'/environments/{os.environ["APPCONFIG_ENVIRONMENT"]}'
            + f'/configurations/{os.environ["APPCONFIG_CONFIGURATION"]}'
        )

    @staticmethod
    def request_app_config_data(url: str):
        config_data = requests.get(url)
        try:
            logger.info(config_data)
            logger.info(config_data.json())
            data = config_data.json()
        except JSONDecodeError as e:
            logger.error(
                str(e),
                {"Result": "Error when retrieving feature flag from AppConfig profile"},
            )
            raise FeatureFlagsException(
                error=LambdaError.FeatureFlagJsonFailure,
                status_code=config_data.status_code,
            )
        if config_data.status_code == 200:
            return data
        if config_data.status_code == 400:
            logger.info(config_data)
            logger.error(
                str(data),
                {"Result": "Error when retrieving feature flag from AppConfig profile"},
            )
            raise FeatureFlagsException(
                error=LambdaError.FeatureFlagNotFound,
                status_code=404,
            )
        else:
            logger.error(
                str(data),
                {"Result": "Error when retrieving feature flag from AppConfig profile"},
            )
            raise FeatureFlagsException(
                error=LambdaError.FeatureFlagFailure,
                status_code=config_data.status_code,
            )

    def get_feature_flags(self) -> dict:
        logger.info("Retrieving all feature flags")

        url = self.app_config_url
        response = self.request_app_config_data(url)
        feature_flags = {key: value["enabled"] for key, value in response.items()}

        return feature_flags

    def get_feature_flags_by_flag(self, flag: str):
        logger.info(f"Retrieving feature flag: {flag}")

        config_url = self.app_config_url
        url = config_url + f"?flag={flag}"

        response = self.request_app_config_data(url)

        return {flag: response["enabled"]}
