import os
import uuid
from datetime import datetime

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, HTTPError, Timeout
from urllib3 import Retry
from utils.audit_logging_setup import LoggingService
from utils.exceptions import NrlApiException

logger = LoggingService(__name__)

NRL_USER_ID = "National-Document-Repository"


class NrlApiService:
    def __init__(self, ssm_service, auth_service):
        self.ssm_service = ssm_service
        self.auth_service = auth_service
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "DELETE", "OPTIONS"],
            backoff_factor=1,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.endpoint = os.getenv("NRL_API_ENDPOINT")
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.end_user_ods_code = self.get_end_user_ods_code()
        self.headers = {
            "Authorization": f"Bearer {self.auth_service.get_active_access_token()}",
            "NHSD-End-User-Organisation-ODS": self.end_user_ods_code,
            "Accept": "application/json",
        }

    def get_end_user_ods_code(self):
        ssm_key_parameter = os.getenv("NRL_END_USER_ODS_CODE")
        return self.ssm_service.get_ssm_parameter(
            ssm_key_parameter, with_decryption=True
        )

    def create_new_pointer(self, body, retry_on_expired: bool = True):
        try:
            self.set_x_request_id()

            response = self.session.post(
                url=self.endpoint, headers=self.headers, json=body
            )
            response.raise_for_status()
            logger.info(
                f"Create pointer response: Status code: ${response.status_code} \n"
                f"Body: {response.json()}, \n"
                f"Date: ${response.headers.get('date', 'No date found.')}"
            )

            logger.info("Successfully created new pointer")
        except (ConnectionError, Timeout, HTTPError) as e:
            logger.error(e.response.content)
            if e.response.status_code == 401 and retry_on_expired:
                self.headers["Authorization"] = (
                    f"Bearer {self.auth_service.get_active_access_token()}"
                )
                self.create_new_pointer(body, retry_on_expired=False)
            else:
                raise NrlApiException("Error while creating new NRL Pointer")

    def get_pointer(self, nhs_number, record_type=None, retry_on_expired: bool = True):
        logger.info(
            f"Get pointer request: URL: {self.endpoint}, \n"
            "HTTP Verb: GET, \n"
            f"ODS Code: {self.end_user_ods_code}, \n"
            f"Datetime: {int(datetime.now().timestamp())}, \n"
            f"UserID: {self.end_user_ods_code} - {NRL_USER_ID}, \n"
        )
        try:
            self.set_x_request_id()
            params = {
                "subject:identifier": f"https://fhir.nhs.uk/Id/nhs-number|{nhs_number}"
            }
            if record_type:
                params["type"] = f"http://snomed.info/sct|{record_type}"
            response = self.session.get(
                url=self.endpoint, params=params, headers=self.headers
            )

            response.raise_for_status()
            logger.info(
                f"Get pointer response: Status code: {response.status_code}, \n"
                f"Body: {response.json()}, \n"
                f"Date: {response.headers.get('date', 'No date found.')}"
            )
            return response.json()
        except HTTPError as e:
            logger.error(e.response.json())
            if e.response.status_code == 401 and retry_on_expired:
                self.headers["Authorization"] = (
                    f"Bearer {self.auth_service.get_active_access_token()}"
                )
                self.get_pointer(nhs_number, record_type, retry_on_expired=False)
            else:
                raise NrlApiException("Error while getting NRL Pointer")

    def delete_pointer(self, nhs_number, record_type):
        search_results = self.get_pointer(nhs_number, record_type).get("entry", [])
        for entry in search_results:
            self.set_x_request_id()
            pointer_id = entry.get("resource", {}).get("id")
            url_endpoint = self.endpoint + f"/{pointer_id}"
            logger.info(
                f"Delete pointer request: URL: {url_endpoint}, \n"
                f"HTTP Verb: DELETE, \n"
                f"ODS Code: {self.end_user_ods_code}, \n"
                f"NHS Number: {nhs_number}, \n"
                f"Datetime: {int(datetime.now().timestamp())}, \n"
                f"UserID: {self.end_user_ods_code} - {NRL_USER_ID} \n"
            )
            try:
                response = self.session.delete(url=url_endpoint, headers=self.headers)
                response.raise_for_status()
                logger.info(
                    f"Delete pointer response: Body: {response.json()}, \n"
                    f"Status Code: {response.status_code}, \n"
                    f"Date: {response.headers.get('date', 'No date found.')}"
                )
            except HTTPError as e:
                logger.error(e.response.json())
                if e.response.status_code == 401:
                    self.headers["Authorization"] = (
                        f"Bearer {self.auth_service.get_active_access_token()}"
                    )
                    self.session.delete(url=self.endpoint, headers=self.headers)
                else:
                    logger.error(f"Unable to delete NRL Pointer: {entry}")
                    continue

    def set_x_request_id(self):
        self.headers["X-Request-ID"] = str(uuid.uuid4())
