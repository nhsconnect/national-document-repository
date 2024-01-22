import json
import os
import random

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

        try:
            with open("services/mock_data/pds_patient_9000000001_X4S4L_pcse.json") as f:
                mock_pds_results.append(json.load(f))
            with open("services/mock_data/pds_patient_9000000002_H81109_gp.json") as f:
                mock_pds_results.append(json.load(f))
            with open("services/mock_data/pds_patient_9730153817_H81109_gp.json") as f:
                mock_pds_results.append(json.load(f))
            with open("services/mock_data/pds_patient_9000000003_H85686_gp.json") as f:
                mock_pds_results.append(json.load(f))
            with open("services/mock_data/pds_patient_9000000025_restricted.json") as f:
                mock_pds_results.append(json.load(f))

        except FileNotFoundError:
            raise PdsErrorException("Error when requesting patient from PDS")

        pds_patient: dict = {}

        for result in mock_pds_results:
            for k, v in result.items():
                if v == nhs_number:
                    pds_patient = result.copy()

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
