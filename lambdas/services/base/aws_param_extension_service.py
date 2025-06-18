import urllib.request
import urllib.error
import os
import json

from botocore import config

from enums.lambda_error import LambdaError
from typing import List
from utils.audit_logging_setup import LoggingService
from utils.lambda_exceptions import LoginException

logger = LoggingService(__name__)


class AwsSsmExtensionService:
    def __init__(self):
        self.aws_session_token = os.environ.get("AWS_SESSION_TOKEN")
        if not self.aws_session_token:
            logger.error(
                LambdaError.EnvMissing.to_str(),
                {"Result": "AWS_SESSION_TOKEN Missing"},
            )
            raise LoginException(500, LambdaError.EnvMissing)

    def get_ssm_parameter(self, parameter_key: str):
        req = urllib.request.Request(
            f"http://localhost:2773/systemsmanager/parameters/get?name={parameter_key}"
        )
        req.add_header("X-Aws-Parameters-Secrets-Token", self.aws_session_token)
        try:
            with urllib.request.urlopen(req) as response:
                config = response.read()
            return json.loads(config)["Parameter"]["Value"]
        except Exception:
            logger.error(
                LambdaError.LoginNoSSM.to_str(),
                {"Result": f"Cannot retrieve Login parameter_key: {parameter_key}"},
            )
            raise LoginException(500, LambdaError.LoginNoSSM)

    def get_ssm_parameters(self, parameters_keys: List[str]):
        return {
            parameter: self.get_ssm_parameter(parameter)
            for parameter in parameters_keys
        }
