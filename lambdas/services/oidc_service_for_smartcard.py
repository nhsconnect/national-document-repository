import logging
import os
from typing import Dict, List, Tuple

import boto3
import jwt
import requests
from models.oidc_models import AccessToken, IdTokenClaimSet
from oauthlib.oauth2 import WebApplicationClient
from requests import Response

from services.oidc_service import OidcService
from utils.exceptions import AuthorisationException

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class OidcServiceForSmartcard(OidcService):

    def token_request(self, event):
        pass

    def fetch_user_org_codes(self, access_token: str, selected_role: str) -> List[str]:
        userinfo = self.fetch_userinfo(access_token)
        nrbac_roles = userinfo.get("nhsid_nrbac_roles", [])
        for role in nrbac_roles:
            if role["person_roleid"] == selected_role:
                return role["org_code"]
        return []

    def fetch_userinfo(self, access_token: AccessToken) -> Dict:
        userinfo_response = requests.get(
            self._oidc_userinfo_url,
            headers={"Authorization": f"Bearer {access_token}, scope nationalrbacaccess"},
            # see if setting scope is actually needed
        )
        if userinfo_response.status_code == 200:
            return userinfo_response.json()
        else:
            logger.error(
                f"Got error response from OIDC provider: {userinfo_response.status_code} "
                f"{userinfo_response.content}"
            )
            raise AuthorisationException("Failed to retrieve userinfo")


