import json
import os

import requests
from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from enums.pds_ssm_parameters import SSMParameter
from requests.models import HTTPError
from services.base.s3_service import S3Service
from services.base.ssm_service import SSMService
from utils.audit_logging_setup import LoggingService
from utils.lambda_exceptions import VirusScanResultException

logger = LoggingService(__name__)


class VirusScanResultService:
    def __init__(self):
        self.s3_service = S3Service()
        self.staging_s3_bucket_name = os.getenv("STAGING_STORE_BUCKET_NAME")
        self.ssm_service = SSMService()

    def get_new_access_token(self):
        try:
            username_key = SSMParameter.VIRUS_API_USER.value
            password_key = SSMParameter.VIRUS_API_PASSWORD.value
            url_key = SSMParameter.VIRUS_API_BASEURL.value
            parameters = [username_key, password_key]

            ssm_response = self.ssm_service.get_ssm_parameters(
                parameters, with_decryption=True
            )
            username = ssm_response[username_key]
            password = ssm_response[password_key]
            base_url = ssm_response[url_key]
            logger.info(f"username: {username}")
            logger.info(f"password: {password}")

            json_login = json.dumps({"username": username, "password": password})
            token_url = base_url + "/api/Token"

            requests.post(
                url=token_url,
                headers={"Content-type": "application/json"},
                data=json_login,
            )

            # TODO: Get access token from param store, if it doesn't work, fetch a new one and set on the param store
            session = requests.Session()
            r = session.post(
                token_url, data=json_login, headers={"Content-type": "application/json"}
            )

            json_response = json.loads(r.text)
            access_token = json_response["accessToken"]
            self.update_ssm_access_token(access_token)
            logger.info(f"new access token: {access_token}")
            return access_token
        except (HTTPError, ClientError) as e:
            logger.error(
                f"{LambdaError.VirusScanNoToken.to_str()}: {str(e)}",
                {"Result": "Virus scan result failed"},
            )
            raise VirusScanResultException(500, LambdaError.VirusScanTokenRequest)

    def update_ssm_access_token(self, access_token):
        parameter_key = SSMParameter.VIRUS_API_ACCESSTOKEN.value
        self.ssm_service.update_ssm_parameter(
            parameter_key=parameter_key,
            parameter_value=access_token,
            parameter_type="SecureString",
        )

    def get_ssm_access_token(self):
        parameters = [
            SSMParameter.VIRUS_API_ACCESSTOKEN.value,
        ]

        access_token = SSMService().get_ssm_parameters(parameters, with_decryption=True)

        logger.info(f"ssm access token: {access_token}")
