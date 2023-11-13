import os
from typing import Dict, List, Tuple

import boto3
import jwt
import requests
from models.oidc_models import AccessToken, IdTokenClaimSet
from oauthlib.oauth2 import WebApplicationClient
from requests import Response
from utils.audit_logging_setup import LoggingService
from utils.exceptions import AuthorisationException

logger = LoggingService(__name__)


class OidcService:
    VERIFY_ALL = {
        "verify_signature": True,
        "verify_exp": True,
        "verify_nbf": True,
        "verify_iat": True,
        "verify_aud": True,
        "verify_iss": True,
    }

    def __init__(self):
        oidc_parameters = self.fetch_oidc_parameters()

        self._client_id = oidc_parameters["OIDC_CLIENT_ID"]
        self._client_secret = oidc_parameters["OIDC_CLIENT_SECRET"]
        self._oidc_issuer_url = oidc_parameters["OIDC_ISSUER_URL"]
        self._oidc_token_url = oidc_parameters["OIDC_TOKEN_URL"]
        self._oidc_userinfo_url = oidc_parameters["OIDC_USER_INFO_URL"]
        self._oidc_callback_uri = oidc_parameters["OIDC_CALLBACK_URL"]
        self._oidc_jwks_url = oidc_parameters["OIDC_JWKS_URL"]

        self.oidc_client = WebApplicationClient(client_id=self._client_id)

    def fetch_tokens(self, auth_code: str) -> Tuple[AccessToken, IdTokenClaimSet]:
        url, headers, body = self.oidc_client.prepare_token_request(
            token_url=self._oidc_token_url,
            code=auth_code,
            redirect_url=self._oidc_callback_uri,
            client_secret=self._client_secret,
        )

        access_token_response = requests.post(url=url, data=body, headers=headers)
        if access_token_response.status_code == 200:
            return self.parse_fetch_tokens_response(access_token_response)
        else:
            logger.error(
                f"Got error response from OIDC provider: {access_token_response.status_code} "
                f"{access_token_response.content}"
            )
            raise AuthorisationException(
                "Failed to retrieve access token from ID Provider"
            )

    def parse_fetch_tokens_response(
        self, fetch_token_response: Response
    ) -> Tuple[AccessToken, IdTokenClaimSet]:
        try:
            response_content = fetch_token_response.json()
            access_token: AccessToken = response_content["access_token"]
            raw_id_token = response_content["id_token"]

            decoded_token = self.validate_and_decode_token(raw_id_token)

            id_token_claims_set: IdTokenClaimSet = IdTokenClaimSet.model_validate(decoded_token)

            return access_token, id_token_claims_set
        except KeyError:
            raise AuthorisationException(
                "Access Token not found in ID Provider's response"
            )

    def validate_and_decode_token(self, signed_token: str) -> Dict:
        try:
            jwks_client = jwt.PyJWKClient(
                self._oidc_jwks_url, cache_jwk_set=True, lifespan=360
            )
            cis2_signing_key = jwks_client.get_signing_key_from_jwt(signed_token)

            return jwt.decode(
                jwt=signed_token,
                key=cis2_signing_key.key,
                algorithms=["RS256"],
                issuer=self._oidc_issuer_url,
                audience=self._client_id,
                options=self.VERIFY_ALL,
            )
        except jwt.exceptions.PyJWTError as err:
            logger.error(err)
            raise AuthorisationException("The given JWT is invalid or expired.")

    def fetch_user_org_codes(
        self, access_token: str, id_token_claim_set: IdTokenClaimSet
    ) -> List[str]:
        userinfo = self.fetch_userinfo(access_token)

        logger.info(f"User info response: {userinfo}")

        nrbac_roles = userinfo.get("nhsid_nrbac_roles", [])

        logger.info(f"nrbac_roles: {nrbac_roles}")

        selected_role = get_selected_roleid(id_token_claim_set)

        logger.info(f"Selected role ID: {selected_role}")

        for role in nrbac_roles:
            logger.info(f"Role: {role}")
            if role["person_roleid"] == selected_role:
                return [role["org_code"]]

        logger.info("No org code found")
        return []

    def fetch_user_role_code(
        self,
        access_token: str,
        id_token_claim_set: IdTokenClaimSet,
        prefix_character: str,
    ) -> str:
        userinfo = self.fetch_userinfo(access_token)
        logger.info(f"User info response: {userinfo}")

        nrbac_roles = userinfo.get("nhsid_nrbac_roles", [])
        logger.info(f"nrbac_roles: {nrbac_roles}")

        selected_role = get_selected_roleid(id_token_claim_set)
        logger.info(f"Selected role ID: {selected_role}")

        role_codes = ""
        for nrbac_role in nrbac_roles:
            if nrbac_role["person_roleid"] == selected_role:
                role_codes = nrbac_role["role_code"]
                break

        if role_codes == "":
            raise AuthorisationException("No role codes found for users selected role")

        role_codes_split = role_codes.split(":")

        for role_code in role_codes_split:
            if role_code[0].upper() == prefix_character.upper():
                return role_code

        raise AuthorisationException(
            f"Role codes have been found for the user but not with prefix {prefix_character.upper()}"
        )

    def fetch_userinfo(self, access_token: AccessToken) -> Dict:
        logger.info(f"Access token for user info request: {access_token}")

        userinfo_response = requests.get(
            self._oidc_userinfo_url,
            headers={
                "Authorization": f"Bearer {access_token}",
            },
        )

        if userinfo_response.status_code == 200:
            return userinfo_response.json()
        else:
            logger.error(
                f"Got error response from OIDC provider: {userinfo_response.status_code} "
                f"{userinfo_response.content}"
            )
            raise AuthorisationException("Failed to retrieve userinfo")

    # TODO Move to SSM service, example in token_handler_ssm_service
    @staticmethod
    def fetch_oidc_parameters():
        parameters_names = [
            "OIDC_CLIENT_ID",
            "OIDC_CLIENT_SECRET",
            "OIDC_ISSUER_URL",
            "OIDC_TOKEN_URL",
            "OIDC_USER_INFO_URL",
            "OIDC_JWKS_URL",
        ]

        ssm_client = boto3.client("ssm")
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


def get_selected_roleid(id_token_claim_set: IdTokenClaimSet):
    return id_token_claim_set.selected_roleid
