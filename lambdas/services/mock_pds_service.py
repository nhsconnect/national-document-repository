import json

from requests import Response
from utils.exceptions import (
    PdsErrorException,
    PatientNotFoundException,
    InvalidResourceIdException,
)

from services.patient_search_service import PatientSearch


class MockPdsApiService(PatientSearch):
    def __init__(self, *args, **kwargs):
        pass

    def pds_request(self, nhsNumber: str, *args, **kwargs) -> Response:
        mock_pds_results: list[dict] = []

        try:
            with open("services/mock_data/pds_patient.json") as f:
                mock_pds_results.append(json.load(f))

            with open("services/mock_data/pds_patient_restricted.json") as f:
                mock_pds_results.append(json.load(f))

        except FileNotFoundError:
            raise PdsErrorException("Error when requesting patient from PDS")

        pds_patient: dict = {}

        for result in mock_pds_results:
            for k, v in result.items():
                if v == nhsNumber:
                    pds_patient = result.copy()

        response = Response()

        if bool(pds_patient):
            response.status_code = 200
            response._content = json.dumps(pds_patient).encode('utf-8')
        else:
            response.status_code = 404

        return response
