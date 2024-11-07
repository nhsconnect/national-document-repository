import os
import uuid

import requests
from requests import HTTPError
from requests.adapters import HTTPAdapter
from urllib3 import Retry
from utils.audit_logging_setup import LoggingService
from utils.exceptions import NrlApiException

logger = LoggingService(__name__)


class NrlApiService:
    def __init__(self, ssm_service, auth_service):
        self.ssm_service = ssm_service
        self.auth_service = auth_service
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            backoff_factor=1,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.endpoint = os.getenv("NRL_API_ENDPOINT")
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.end_user_ods_code = self.__get_end_user_ods_code()
        self.headers = {
            "Authorization": f"Bearer {self.auth_service.create_access_token()}",
            "NHSD-End-User-Organisation-ODS": self.end_user_ods_code,
        }

    def __get_end_user_ods_code(self):
        ssm_key_parameter = os.getenv("NRL_END_USER_ODS_CODE")
        return self.ssm_service.get_ssm_parameter(
            ssm_key_parameter, with_decryption=True
        )

    def create_new_pointer(self, body, retry_on_expired: bool = True):
        try:
            self.set_x_request_id()
            self.headers["Accept"] = "application/json"
            response = self.session.post(
                url=self.endpoint, headers=self.headers, json=body
            )
            response.raise_for_status()
            logger.info("Successfully created new pointer")
            self.headers.pop("Accept")
        except HTTPError as e:
            logger.error(e.response)
            if e.response.status_code == 429 and retry_on_expired:
                self.headers["Authorization"] = (
                    f"Bearer {self.auth_service.create_access_token()}"
                )
                self.create_new_pointer(body, retry_on_expired=False)
            else:
                raise NrlApiException("Error while creating new NRL Pointer")

    def update_pointer(self):
        self.set_x_request_id()

    def delete_pointer(self):
        self.set_x_request_id()

    def set_x_request_id(self):
        self.headers["X-Request-ID"] = str(uuid.uuid4())
