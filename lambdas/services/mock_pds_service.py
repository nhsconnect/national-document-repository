import json
import os
import random
from glob import glob

from requests import Response
from services.patient_search_service import PatientSearch
from utils.exceptions import PdsErrorException


class MockPdsApiService(PatientSearch):
    def __init__(self, *args, **kwargs):
        pass

    def pds_request(self, nhs_number: str, *args, **kwargs) -> Response:
        mock_pds_results: list[dict] = []

        if os.getenv("MOCK_PDS_TOO_MANY_REQUESTS_ERROR") == "true":
            if random.random() < 0.333:
                return self.too_many_requests_response()

        parent_dir_of_this_file = os.path.join(os.path.dirname(__file__), os.pardir)
        all_mock_files = glob(
            "services/mock_data/*.json", root_dir=parent_dir_of_this_file
        )

        try:
            for file in all_mock_files:
                with open(file) as f:
                    mock_pds_results.append(json.load(f))

        except FileNotFoundError:
            raise PdsErrorException("Error when requesting patient from PDS")

        pds_patient: dict = {}

        for result in mock_pds_results:
            mock_patient_nhs_number = result.get("id")
            if mock_patient_nhs_number == nhs_number:
                pds_patient = result
                break

        response = Response()

        if bool(pds_patient):
            response.status_code = 200
            response._content = json.dumps(pds_patient).encode("utf-8")
        else:
            response.status_code = 404

        return response

    def too_many_requests_response(self) -> Response:
        response = Response()
        response.status_code = 429
        response._content = b"Too Many Requests"
        return response
