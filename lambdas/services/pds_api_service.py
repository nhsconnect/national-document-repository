import json
import logging
import time
import uuid

import jwt
import requests
from botocore.exceptions import ClientError
from enums.pds_ssm_parameters import SSMParameter
from requests.models import HTTPError
from services.patient_search_service import PatientSearch
from utils.exceptions import PdsErrorException

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class PdsApiService(PatientSearch):
    def __init__(self, ssm_service):
        self.ssm_service = ssm_service

    def pds_request(self, nshNumber: str, retry_on_expired: bool):
        try:
            endpoint, access_token_response = self.get_parameters_for_pds_api_request()
            access_token_response = json.loads(access_token_response)
            access_token = access_token_response["access_token"]
            access_token_expiration = (
                int(access_token_response["expires_in"])
                + int(access_token_response["issued_at"]) / 1000
            )
            time_safety_margin_seconds = 10
            if time.time() - access_token_expiration > time_safety_margin_seconds:
                access_token = self.get_new_access_token()

            x_request_id = str(uuid.uuid4())

            authorization_header = {
                "Authorization": f"Bearer {access_token}",
                "X-Request-ID": x_request_id,
            }

            url_endpoint = endpoint + "Patient/" + nshNumber
            pds_response = requests.get(url=url_endpoint, headers=authorization_header)
            if pds_response.status_code == 401 and retry_on_expired:
                return self.pds_request(nshNumber, retry_on_expired=False)
            return pds_response

        except ClientError as e:
            logger.error(f"Error when getting ssm parameters {e}")
            raise PdsErrorException("Failed to preform patient search")

    def get_new_access_token(self):
        logger.info("Getting new PDS access token")
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
            logger.error(f"Issue while creating new access token: {e.response}")
            raise PdsErrorException("Error accessing PDS API")
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

    def get_parameters_for_pds_api_request(self):
        parameters = [
            SSMParameter.PDS_API_ENDPOINT.value,
            SSMParameter.PDS_API_ACCESS_TOKEN.value,
        ]
        ssm_response = self.ssm_service.get_ssm_parameters(
            parameters_keys=parameters, with_decryption=True
        )
        return ssm_response[parameters[0]], ssm_response[parameters[1]]

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
