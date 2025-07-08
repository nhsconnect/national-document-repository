import json
import os
import random
from glob import glob

from requests import Response
from services.patient_search_service import PatientSearch
from utils.exceptions import PdsErrorException


class MockPdsApiService(PatientSearch):
    def __init__(self, always_pass_mock: bool = False, *args, **kwargs):
        self.always_pass_mock = always_pass_mock
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
                with open(file) as mock_file:
                    mock_pds_results.append(json.load(mock_file))

        except FileNotFoundError:
            raise PdsErrorException("Error when requesting patient from PDS")

        pds_patient: dict = {}
        response = Response()
        if self.always_pass_mock:
            mock_file_name = "pds_patient_9000000068_M85143_gp.json"
            file_path = os.path.join(
                parent_dir_of_this_file, "services", "mock_data", mock_file_name
            )
            try:
                with open(file_path) as open_file:
                    pds_patient = json.load(open_file)
            except FileNotFoundError:
                raise PdsErrorException(f"Mock file '{mock_file_name}' not found")
            pds_patient["id"] = nhs_number
            pds_patient["identifier"][0]["value"] = nhs_number
            print(f"pds_patient={pds_patient}")
        else:
            for result in mock_pds_results:
                mock_patient_nhs_number = result.get("id")
                if mock_patient_nhs_number == nhs_number:
                    pds_patient = result
                    break

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
