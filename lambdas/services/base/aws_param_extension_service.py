import urllib.request
import os
import json


class AwsSsmExtensionService:
    def __init__(self):
        self.aws_session_token = os.environ.get("AWS_SESSION_TOKEN")

    def get_ssm_parameter(self, parameter_key: str):
        req = urllib.request.Request(
            f"http://localhost:2773/systemsmanager/parameters/get?name={parameter_key}"
        )
        req.add_header("X-Aws-Parameters-Secrets-Token", self.aws_session_token)
        config = urllib.request.urlopen(req).read()

        return json.loads(config)

    def get_ssm_parameters(self, parameters_keys: list[str]):
        return {
            parameter: self.get_ssm_parameter(parameter)
            for parameter in parameters_keys
        }
