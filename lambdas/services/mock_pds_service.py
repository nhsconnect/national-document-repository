import json

from models.pds_models import PatientDetails
from requests import Response
from utils.utilities import validate_id
from utils.exceptions import PdsErrorException
from models.pds_models import Patient


class MockPdsApiService:
    def fetch_patient_details(self, nhs_number: str) -> PatientDetails:
        validate_id(nhs_number)

        response = self.fake_pds_request(nhs_number)

        if response.status_code == 200:
            patient = Patient.model_validate(response.content)
            patient_details = patient.get_patient_details(nhs_number)
            return patient_details

        raise PdsErrorException("Error when requesting patient from PDS")


    def fake_pds_request(self, nhsNumber: str) -> Response:
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
            response._content = pds_patient
        else:
            response.status_code = 404

        return response