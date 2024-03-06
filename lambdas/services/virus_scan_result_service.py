import json
import os

import requests
from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from enums.pds_ssm_parameters import SSMParameter
from requests.models import HTTPError
from services.base.ssm_service import SSMService
from utils.audit_logging_setup import LoggingService
from utils.lambda_exceptions import VirusScanResultException

logger = LoggingService(__name__)

FAIL_SCAN = "Virus scan result failed"


class VirusScanResultService:
    def __init__(self):
        self.staging_s3_bucket_name = os.getenv("STAGING_STORE_BUCKET_NAME")
        self.ssm_service = SSMService()
        self.username = ""
        self.password = ""
        self.base_url = ""
        self.access_token = ""

    def prepare_request(self, file_ref):
        try:
            self.get_ssm_parameters_for_request_access_token()
            self.virus_scan_request(file_ref, retry_on_expired=True)
        except ClientError as e:
            logger.error(
                f"{LambdaError.VirusScanAWSFailure.to_str()}: {str(e)}",
                {"Result": FAIL_SCAN},
            )
            raise VirusScanResultException(500, LambdaError.VirusScanAWSFailure)

    def virus_scan_request(self, file_ref: str, retry_on_expired: bool):
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self.access_token,
            }
            scan_url = self.base_url + "/api/Scan/Existing"
            json_data_request = {
                "container": self.staging_s3_bucket_name,
                "objectPath": file_ref,
            }
            logger.info(json_data_request)

            response = requests.post(
                url=scan_url, data=json.dumps(json_data_request), headers=headers
            )
            if response.status_code == 401 and retry_on_expired:
                self.get_new_access_token()
                return self.virus_scan_request(file_ref, retry_on_expired=False)
            response.raise_for_status()

            parsed = response.json()

            if parsed["result"] == "Clean":
                logger.info(
                    "Virus scan request succeeded",
                    {"Result": "Virus scan request succeeded"},
                )
                return
            else:
                logger.info(
                    "File is not clean",
                    {"Result": FAIL_SCAN},
                )
                raise VirusScanResultException(400, LambdaError.VirusScanUnclean)

        except HTTPError:
            logger.info(
                "Virus scan request failed",
                {"Result": FAIL_SCAN},
            )
            raise VirusScanResultException(400, LambdaError.VirusScanTokenRequest)

    def get_new_access_token(self):
        try:
            logger.info(f"username: {self.username}")
            logger.info(f"password: {self.password}")

            json_login = json.dumps(
                {"username": self.username, "password": self.password}
            )
            token_url = self.base_url + "/api/Token"

            response = requests.post(
                url=token_url,
                headers={"Content-type": "application/json"},
                data=json_login,
            )

            response.raise_for_status()
            logger.info(response.json())
            new_access_token = response.json()["accessToken"]

            self.update_ssm_access_token(new_access_token)
            logger.info(f"new access token: {new_access_token}")
            self.access_token = new_access_token
        except HTTPError as e:
            logger.error(
                f"{LambdaError.VirusScanNoToken.to_str()}: {str(e)}",
                {"Result": FAIL_SCAN},
            )
            raise VirusScanResultException(500, LambdaError.VirusScanTokenRequest)

    def update_ssm_access_token(self, access_token):
        parameter_key = SSMParameter.VIRUS_API_ACCESSTOKEN.value
        self.ssm_service.update_ssm_parameter(
            parameter_key=parameter_key,
            parameter_value=access_token,
            parameter_type="SecureString",
        )

    def get_ssm_parameters_for_request_access_token(self):
        access_token_key = SSMParameter.VIRUS_API_ACCESSTOKEN.value
        username_key = SSMParameter.VIRUS_API_USER.value
        password_key = SSMParameter.VIRUS_API_PASSWORD.value
        url_key = SSMParameter.VIRUS_API_BASEURL.value

        parameters = [username_key, password_key, url_key, access_token_key]

        ssm_response = self.ssm_service.get_ssm_parameters(
            parameters, with_decryption=True
        )
        self.username = ssm_response[username_key]
        self.password = ssm_response[password_key]
        self.base_url = ssm_response[url_key]
        self.access_token = ssm_response[access_token_key]
