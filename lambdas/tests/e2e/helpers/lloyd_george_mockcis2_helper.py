import json
import logging
import os
from urllib.parse import parse_qs, quote, urlparse

import requests


class LloydGeorgeMockcis2Helper:
    def __init__(self, ods, repository_role):
        self.mock_key = os.environ.get("MOCK_CIS2_KEY") or ""
        self.api_endpoint = os.environ.get("NDR_API_ENDPOINT")
        self.ods = ods
        self.repository_role = repository_role

        pass

    def generate_mockcis2_token(self):
        self.get_state()
        self.setup_token_request_uri()
        self.get_auth_token()
        pass

    def get_state(self):
        login_response = requests.get(
            f"https://{self.api_endpoint}/Auth/Login", allow_redirects=False
        )
        location = login_response.headers.get("Location")

        parsed_url = urlparse(location)

        parsed_qs = parse_qs(str(parsed_url.query))
        state_value = parsed_qs.get("state", [None])[0]
        self.state = state_value

    def setup_token_request_uri(self):
        token_request_param = {
            "key": self.mock_key,
            "odsCode": self.ods,
            "repositoryRole": self.repository_role,
        }

        token_request_params_json = json.dumps(token_request_param)
        encoded_param = quote(str(token_request_params_json))
        self.encoded_login_parameter = encoded_param

    def get_auth_token(self):
        token_response = requests.get(
            f"https://{self.api_endpoint}/Auth/TokenRequest",
            params={"code": self.encoded_login_parameter, "state": self.state},
        )
        token_response_json = token_response.json()
        logging.info(token_response_json)
        self.user_token = token_response_json["authorisation_token"]
        self.user_role = token_response_json["role"]
