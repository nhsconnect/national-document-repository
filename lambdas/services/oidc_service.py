import logging
import os
from typing import Dict, List, Tuple

import boto3
import jwt
import requests
from models.oidc_models import AccessToken, IdTokenClaimSet
from oauthlib.oauth2 import WebApplicationClient
from requests import Response
from utils.exceptions import AuthorisationException

logger = logging.getLogger()
logger.setLevel(logging.INFO)


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

            id_token_claims_set: IdTokenClaimSet = IdTokenClaimSet.model_validate(
                self.validate_and_decode_token(raw_id_token)
            )

            self.selected_role_id = id_token_claims_set.selected_roleid

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

    def fetch_user_org_codes(self, access_token: str, selected_role: str) -> List[str]:
        raise NotImplementedError

    def fetch_userinfo(self, access_token: AccessToken) -> Dict:
        raise NotImplementedError