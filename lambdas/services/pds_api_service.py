import logging
import uuid
from time import time

import jwt
import requests
from models.pds_models import Patient, PatientDetails
from requests.models import Response, HTTPError
from utils.exceptions import (InvalidResourceIdException,
                              PatientNotFoundException, PdsErrorException)
from utils.utilities import validate_id

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class PdsApiService:
    def __init__(self, ssm_service):
        self.ssm_service = ssm_service

    def fetch_patient_details(self, nhs_number: str,) -> PatientDetails:
        validate_id(nhs_number)
        response = self.pds_request(nhs_number, retry_on_expired=True)
        return self.handle_response(response, nhs_number)

    def handle_response(self, response: Response, nhs_number: str) -> PatientDetails:
        if response.status_code == 200:
            patient = Patient.model_validate(response.json())
            patient_details = patient.get_patient_details(nhs_number)
            return patient_details

        if response.status_code == 404:
            raise PatientNotFoundException(
                "Patient does not exist for given NHS number"
            )

        if response.status_code == 400:
            raise InvalidResourceIdException("Invalid NHS number")

        raise PdsErrorException("Error when requesting patient from PDS")

    def pds_request(self, nshNumber: str, retry_on_expired: bool):
        endpoint, access_token_response = self.get_parameters_for_pds_api_request()
        access_token = access_token_response['access_token']
        access_token_expiration = access_token_response['expires_at']
        if access_token_expiration < time():
            access_token = self.get_new_access_token()

        x_request_id = str(uuid.uuid4())

        authorization_header = {"Authorization" : f"Bearer {access_token}",
                                "X-Request-ID" : x_request_id}

        url_endpoint = endpoint + 'Patient/' + nshNumber
        pds_response = requests.get(url=url_endpoint, headers=authorization_header)

        if pds_response.status_code == 401 & retry_on_expired:
            return self.pds_request(nshNumber, retry_on_expired=False)
        return pds_response


    def get_new_access_token(self):
        try:
            access_token_ssm_parameter = self.get_parameters_for_new_access_token()
            jwt_token = self.create_jwt_token_for_new_access_token_request(access_token_ssm_parameter)
            nhs_oauth_endpoint = access_token_ssm_parameter["/prs/dev/user-input/nhs-oauth-endpoint"]
            nhs_oauth_response = self.request_new_access_token(jwt_token, nhs_oauth_endpoint)
            nhs_oauth_response.raise_for_status()
            token_access_response = nhs_oauth_response.json()
            token_access_response['expires_at'] = self.change_token_expires_in_to_expires_at(token_access_response['expires_in'])
            self.update_access_token_ssm(token_access_response)
        except HTTPError as e:
            logger.error(f"Issue while creating new access token: {e.response}")
            raise PdsErrorException("Error accessing PDS API")
        return token_access_response['access_token']

    def get_parameters_for_new_access_token(self):
        parameters = ["/prs/dev/user-input/nhs-oauth-endpoint", "/prs/dev/user-input/pds-fhir-kid", "/prs/dev/user-input/nhs-api-key", "/prs/dev/user-input/pds-fhir-private-key"]
        return self.ssm_service.get_ssm_parameters(parameters, with_decryption=True)

    def update_access_token_ssm(self, parameter_value: str):
        parameter_key = "/prs/dev-ndr/pds-fhir-access-token"
        self.ssm_service.update_ssm_parameter(parameter_key=parameter_key, parameter_value=parameter_value, parameter_type='SecureString')

    def get_parameters_for_pds_api_request(self):
        parameters = ["/prs/dev/user-input/pds-fhir-endpoint", "/prs/dev-ndr/pds-fhir-access-token"]
        ssm_response = self.ssm_service.get_ssm_parameters(parameters, with_decryption=True)
        return ssm_response[parameters[0]], ssm_response[parameters[1]]

    def create_jwt_token_for_new_access_token_request(self, access_token_ssm_parameter):
        nhs_oauth_endpoint = access_token_ssm_parameter["/prs/dev/user-input/nhs-oauth-endpoint"]
        kid = access_token_ssm_parameter["/prs/dev/user-input/pds-fhir-kid"]
        nhs_key = access_token_ssm_parameter["/prs/dev/user-input/nhs-api-key"]
        pds_key = access_token_ssm_parameter["/prs/dev/user-input/pds-fhir-private-key"]
        payload = {
            "iss": nhs_key,
            "sub": nhs_key,
            "aud": nhs_oauth_endpoint,
            "jti": str(uuid.uuid4()),
            "exp": int(time()) + 300
        }
        return jwt.encode(payload, pds_key, algorithm="RS512", headers={"kid": kid})

    def request_new_access_token(self, jwt_token, nhs_oauth_endpoint):
        access_token_headers = {
            "content-type": "application/x-www-form-urlencoded"
        }
        access_token_data = {
            "grant_type" : "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": jwt_token
        }
        return requests.post(url=nhs_oauth_endpoint, headers=access_token_headers, data=access_token_data)

    def change_token_expires_in_to_expires_at(self, token_access_expires_in: int):
        safety_time_delta = 5
        return token_access_expires_in + time() - safety_time_delta

