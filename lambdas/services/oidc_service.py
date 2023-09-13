import logging
import os
from typing import Dict, List

import boto3
import requests
from oauthlib.oauth2 import WebApplicationClient

from utils.exceptions import AuthorisationException

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class OidcService:
    def __init__(self):
        oidc_parameters = self.fetch_oidc_parameters()

        logger.info(f"Initialising OIDC service with parameter: {oidc_parameters}")

        self._client_id = oidc_parameters["OIDC_CLIENT_ID"]
        self._client_secret = oidc_parameters["OIDC_CLIENT_SECRET"]
        self._oidc_issuer_url = oidc_parameters["OIDC_ISSUER_URL"]
        self._oidc_token_url = oidc_parameters["OIDC_TOKEN_URL"]
        self._oidc_userinfo_url = oidc_parameters["OIDC_USER_INFO_URL"]
        self._oidc_callback_uri = oidc_parameters["OIDC_CALLBACK_URL"]
        self.scope = "openid profile nationalrbacaccess associatedorgs"

        self.oidc_client = WebApplicationClient(client_id=self._client_id)

    def fetch_access_token(self, auth_code: str) -> str:
        url, headers, body = self.oidc_client.prepare_token_request(
            token_url=self._oidc_token_url,
            code=auth_code,
            redirect_url=self._oidc_callback_uri,
            client_secret=self._client_secret,
        )

        access_token_response = requests.post(url=url, data=body, headers=headers)
        if access_token_response.status_code == 200:
            try:
                access_token = access_token_response.json()["access_token"]
                return access_token
            except KeyError:
                raise AuthorisationException(
                    "Access Token not found in provider's response"
                )
        else:
            logger.error(
                f"Got error response from OIDC provider: {access_token_response.status_code} "
                f"{access_token_response.content}"
            )
            raise AuthorisationException("Failed to retrieve access token")

    def fetch_user_org_codes(self, access_token: str) -> List[str]:
        userinfo = self.fetch_userinfo(access_token)
        return self.extract_org_codes(userinfo)

    def fetch_userinfo(self, access_token: str) -> Dict:
        userinfo_response = requests.get(
            self._oidc_userinfo_url,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if userinfo_response.status_code == 200:
            return userinfo_response.json()
        else:
            logger.error(
                f"Got error response from OIDC provider: {userinfo_response.status_code} "
                f"{userinfo_response.content}"
            )
            raise AuthorisationException("Failed to retrieve userinfo")

    def extract_org_codes(self, userinfo: Dict) -> List[str]:
        nrbac_roles = userinfo.get("nhsid_nrbac_roles", [])
        return [role["org_code"] for role in nrbac_roles if "org_code" in role]

    def fetch_oidc_parameters(self):
        parameters_names = [
            "OIDC_CLIENT_ID",
            "OIDC_CLIENT_SECRET",
            "OIDC_ISSUER_URL",
            "OIDC_TOKEN_URL",
            "OIDC_USER_INFO_URL",
        ]

        ssm_client = boto3.client("ssm", region_name="eu-west-2")
        ssm_response = ssm_client.get_parameters(
            Names=parameters_names, WithDecryption=True
        )
        oidc_parameters = {
            parameter["Name"]: parameter["Value"]
            for parameter in ssm_response["Parameters"]
        }

        # Callback url is different in sandbox/dev/test. This env var is to be supplied by terraform.
        oidc_parameters["OIDC_CALLBACK_URL"] = os.environ["OIDC_CALLBACK_URL"]

        return oidc_parameters
