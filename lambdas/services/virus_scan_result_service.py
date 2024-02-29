import json
import os

import requests
from enums.lambda_error import LambdaError
from enums.pds_ssm_parameters import SSMParameter
from services.base.s3_service import S3Service
from services.base.ssm_service import SSMService
from utils.audit_logging_setup import LoggingService
from utils.lambda_exceptions import VirusScanResultException

logger = LoggingService(__name__)


class VirusScanResultService:
    def __init__(self):
        self.s3_service = S3Service()
        self.staging_s3_bucket_name = os.getenv("STAGING_STORE_BUCKET_NAME")
        self.base_url = "https://ndr-dev-vcapi.cloudstoragesecapp.com"

    def fetch_new_access_token(self):
        try:
            parameters = [
                SSMParameter.VIRUS_API_USER.value,
                SSMParameter.VIRUS_API_PASSWORD.value,
            ]

            username, password = SSMService().get_ssm_parameters(
                parameters, with_decryption=True
            )

            logger.info(f"username: {username}")
            logger.info(f"password: {password}")

            json_login = json.dumps({"username": username, "password": password})
            token_url = self.base_url + "/api/Token"
            # TODO: Get access token from param store, if it doesn't work, fetch a new one and set on the param store
            session = requests.Session()
            r = session.post(
                token_url, data=json_login, headers={"Content-type": "application/json"}
            )

            json_response = json.loads(r.text)
            access_token = json_response["accessToken"]
            logger.info(f"new access token: {access_token}")
            return access_token
        except Exception as e:
            logger.error(
                f"{LambdaError.VirusScanNoToken.to_str()}: {str(e)}",
                {"Result": "Virus scan result failed"},
            )
            raise VirusScanResultException(500, LambdaError.VirusScanTokenRequest)

    def get_ssm_access_token(self):
        parameters = [
            SSMParameter.VIRUS_API_ACCESSTOKEN.value,
        ]

        access_token = SSMService().get_ssm_parameters(parameters, with_decryption=True)

        logger.info(f"ssm access token: {access_token}")
