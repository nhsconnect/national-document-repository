import datetime
import json
import random
from typing import Dict, Tuple, override

from models.oidc_models import AccessToken, IdTokenClaimSet
from scripts.mns_subscription import ssm_service
from services.base.ssm_service import SSMService
from utils.audit_logging_setup import LoggingService
from utils.exceptions import OidcApiException
from utils.request_context import request_context

logger = LoggingService(__name__)


class MockOidcService:
    VERIFY_ALL = {
        "verify_signature": True,
        "verify_exp": True,
        "verify_nbf": True,
        "verify_iat": True,
        "verify_aud": True,
        "verify_iss": True,
    }

    AAL_EXEMPT_ENVIRONMENTS = ["dev", "test", "pre-prod"]

    def __init__(self):
        self._client_id = ""
        self._client_secret = ""
        self._oidc_issuer_url = ""
        self._oidc_token_url = ""
        self._oidc_userinfo_url = ""
        self._oidc_callback_uri = ""
        self._oidc_jwks_url = ""
        self.oidc_client = None
        self.environment = ""
        self.ssm_prefix = getattr(request_context, "auth_ssm_prefix", "")
        self.ssm_service = SSMService()

    @override
    def fetch_tokens(self, auth_code: str) -> Tuple[AccessToken, IdTokenClaimSet]:

        deserialised_auth_code = json.loads(auth_code)
        key = deserialised_auth_code["key"]
        repository_role = deserialised_auth_code["repositoryRole"]
        role_code_string_list = ssm_service.get_ssm_parameter(
            "auth/smartcard/role/" + repository_role
        )
        role_code = role_code_string_list.split(",")[0]
        ssm_key = ssm_service.get_ssm_parameter(self.ssm_prefix + "KEY")
        expiry_time = int(
            (datetime.datetime.now() + datetime.timedelta(minutes=30)).timestamp()
        )

        if key == ssm_key:
            id_token_claimset = IdTokenClaimSet("Mock", "Mock1", expiry_time, role_code)
            access_token = AccessToken(auth_code)
            return access_token, id_token_claimset
        logger.error("Provided key does not match Key stored in SSM")
        raise OidcApiException("Failed to retrieve access token from ID Provider")

    @override
    def fetch_userinfo(self, access_token: AccessToken) -> Dict:
        """
        Fetch user information from the OIDC provider.

        Args:
            access_token: The OAuth access token

        Returns:
            User information as a dictionary

        Raises:
            OidcApiException: If the request fails
        """
        logger.info(f"Access token for user info request: {access_token}")

        deserialised_access_token = json.loads(access_token)
        ods_code, repository_role = (
            deserialised_access_token["odsCode"],
            deserialised_access_token["repositoryRole"],
        )
        role_code = ssm_service.get_ssm_parameter(
            "auth/smartcard/role/" + repository_role
        )

        if deserialised_access_token:
            user_info = {
                "nhsid_nrbac_roles": [
                    {
                        "person_roleid": role_code,  # TODO: Replace role_code with an actual selected_role_id
                        "org_code": ods_code,
                    }
                ],
                "nhsid_useruid": random.randint(
                    10000, 99999
                ),  # TODO: What value should this be set to?
            }
            logger.info(f"User info: {user_info}")
            return user_info
        else:
            logger.error("Got error response from OIDC provider:")
            raise OidcApiException("Failed to retrieve userinfo")
