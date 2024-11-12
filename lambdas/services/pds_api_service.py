import uuid
from json import JSONDecodeError

import requests
from botocore.exceptions import ClientError
from enums.pds_ssm_parameters import SSMParameter
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, HTTPError, Timeout
from services.patient_search_service import PatientSearch
from urllib3 import Retry
from utils.audit_logging_setup import LoggingService
from utils.exceptions import PdsErrorException, PdsTooManyRequestsException

logger = LoggingService(__name__)


class PdsApiService(PatientSearch):
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

        self.session = requests.Session()
        self.session.mount("https://", adapter)

    def pds_request(self, nhs_number: str, retry_on_expired: bool):
        try:
            endpoint = self.get_endpoint_for_pds_api_request()
            access_token = self.auth_service.get_active_access_token()

            x_request_id = str(uuid.uuid4())

            authorization_header = {
                "Authorization": f"Bearer {access_token}",
                "X-Request-ID": x_request_id,
            }

            url_endpoint = endpoint + "Patient/" + nhs_number
            pds_response = self.session.get(
                url=url_endpoint, headers=authorization_header
            )

            if pds_response.status_code == 401 and retry_on_expired:
                return self.pds_request(nhs_number, retry_on_expired=False)

            return pds_response

        except (ClientError, JSONDecodeError) as e:
            logger.error(str(e), {"Result": "Error when getting ssm parameters"})
            raise PdsErrorException("Failed to perform patient search")

        except (ConnectionError, Timeout, HTTPError) as e:
            logger.error(str(e), {"Result": "Error when calling PDS"})
            raise PdsTooManyRequestsException("Failed to perform patient search")

    def get_endpoint_for_pds_api_request(self):
        parameter = SSMParameter.PDS_API_ENDPOINT.value

        ssm_response = self.ssm_service.get_ssm_parameter(
            parameter_key=parameter, with_decryption=True
        )
        return ssm_response
