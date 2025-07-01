import datetime
import json
import random
from typing import Dict, Tuple
from urllib.parse import unquote

from models.oidc_models import AccessToken, IdTokenClaimSet
from services.base.ssm_service import SSMService
from utils.audit_logging_setup import LoggingService
from utils.exceptions import OidcApiException
from utils.request_context import request_context

logger = LoggingService(__name__)


class MockOidcService:
    def __init__(self):
        self.ssm_prefix = getattr(request_context, "auth_ssm_prefix", "")
        self.ssm_service = SSMService()

    def fetch_tokens(self, auth_code: str) -> Tuple[AccessToken, IdTokenClaimSet]:
        decoded_auth_code = unquote(auth_code)
        deserialised_auth_code = json.loads(decoded_auth_code)

        key = deserialised_auth_code["key"]
        ssm_key = self.ssm_service.get_ssm_parameter(self.ssm_prefix + "KEY")

        if key == ssm_key:
            expiry_time = int(
                (datetime.datetime.now() + datetime.timedelta(minutes=30)).timestamp()
            )
            id_token_claimset = IdTokenClaimSet(
                sub="MOCK_SUB",
                sid="MOCK_SID",
                exp=expiry_time,
                selected_roleid="MOCK_SELECTED_ROLEID",
            )
            access_token = AccessToken(auth_code)
            return access_token, id_token_claimset
        else:
            logger.error("Provided key does not match key stored in SSM")
            raise OidcApiException(
                "Failed to retrieve access token from mock_oidc_service"
            )

    def fetch_userinfo(self, access_token: AccessToken) -> Dict:
        decoded_access_token = unquote(access_token)
        deserialised_access_token = json.loads(decoded_access_token)

        try:
            ods_code, repository_role = (
                deserialised_access_token["odsCode"],
                deserialised_access_token["repositoryRole"],
            )

            if deserialised_access_token:
                role_code_string_list = self.ssm_service.get_ssm_parameter(
                    f"/auth/smartcard/role/{repository_role}"
                )
                role_code = role_code_string_list.split(",")[0]

                user_info = {
                    "nhsid_nrbac_roles": [
                        {
                            "person_roleid": "MOCK_SELECTED_ROLEID",
                            "org_code": ods_code,
                            "role_code": role_code,
                        }
                    ],
                    "nhsid_useruid": random.randint(10000, 99999),
                }

                logger.info(f"User info: {user_info}")
                return user_info
            else:
                logger.error("Got error response from mock_oidc_service:")
                raise OidcApiException("Failed to retrieve userinfo")
        except KeyError as error:
            logger.error(f"Error while fetching userinfo: {error}")
            raise OidcApiException("Failed to retrieve userinfo")
