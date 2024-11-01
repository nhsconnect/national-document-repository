import json
import time
import uuid

import jwt
import requests
from enums.pds_ssm_parameters import SSMParameter
from requests.exceptions import HTTPError
from utils.audit_logging_setup import LoggingService
from utils.exceptions import OAuthErrorException

logger = LoggingService(__name__)


class NhsOauthService:
    def __init__(self, ssm_service):
        self.ssm_service = ssm_service()

    def create_access_token(self):
        access_token_response = self.get_current_access_token()
        access_token_response = json.loads(access_token_response)
        access_token = access_token_response["access_token"]
        access_token_expiration = (
            int(access_token_response["expires_in"])
            + int(access_token_response["issued_at"]) / 1000
        )
        time_safety_margin_seconds = 10
        remaining_time_before_expiration = access_token_expiration - time.time()
        if remaining_time_before_expiration < time_safety_margin_seconds:
            access_token = self.get_new_access_token()

        return access_token

    def get_new_access_token(self):
        logger.info("Getting new OAuth access token")
        try:
            access_token_ssm_parameter = self.get_parameters_for_new_access_token()
            jwt_token = self.create_jwt_token_for_new_access_token_request(
                access_token_ssm_parameter
            )
            nhs_oauth_endpoint = access_token_ssm_parameter[
                SSMParameter.NHS_OAUTH_ENDPOINT.value
            ]
            nhs_oauth_response = self.request_new_access_token(
                jwt_token, nhs_oauth_endpoint
            )
            nhs_oauth_response.raise_for_status()
            token_access_response = nhs_oauth_response.json()
            self.update_access_token_ssm(json.dumps(token_access_response))
        except HTTPError as e:
            logger.error(
                e.response, {"Result": "Issue while creating new access token"}
            )
            raise OAuthErrorException("Error creating oauth access token")
        return token_access_response["access_token"]

    def get_parameters_for_new_access_token(self):
        parameters = [
            SSMParameter.NHS_OAUTH_ENDPOINT.value,
            SSMParameter.PDS_KID.value,
            SSMParameter.NHS_OAUTH_KEY.value,
            SSMParameter.PDS_API_KEY.value,
        ]
        return self.ssm_service.get_ssm_parameters(parameters, with_decryption=True)

    def update_access_token_ssm(self, parameter_value: str):
        parameter_key = SSMParameter.PDS_API_ACCESS_TOKEN.value
        self.ssm_service.update_ssm_parameter(
            parameter_key=parameter_key,
            parameter_value=parameter_value,
            parameter_type="SecureString",
        )

    def get_current_access_token(self):
        parameter = SSMParameter.PDS_API_ACCESS_TOKEN.value

        ssm_response = self.ssm_service.get_ssm_parameter(
            parameter, with_decryption=True
        )
        return ssm_response

    def create_jwt_token_for_new_access_token_request(
        self, access_token_ssm_parameters
    ):
        nhs_oauth_endpoint = access_token_ssm_parameters[
            SSMParameter.NHS_OAUTH_ENDPOINT.value
        ]
        kid = access_token_ssm_parameters[SSMParameter.PDS_KID.value]
        nhs_key = access_token_ssm_parameters[SSMParameter.NHS_OAUTH_KEY.value]
        pds_key = access_token_ssm_parameters[SSMParameter.PDS_API_KEY.value]
        payload = {
            "iss": nhs_key,
            "sub": nhs_key,
            "aud": nhs_oauth_endpoint,
            "jti": str(uuid.uuid4()),
            "exp": int(time.time()) + 300,
        }
        return jwt.encode(payload, pds_key, algorithm="RS512", headers={"kid": kid})

    def request_new_access_token(self, jwt_token, nhs_oauth_endpoint):
        access_token_headers = {"content-type": "application/x-www-form-urlencoded"}
        access_token_data = {
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": jwt_token,
        }
        return requests.post(
            url=nhs_oauth_endpoint, headers=access_token_headers, data=access_token_data
        )
