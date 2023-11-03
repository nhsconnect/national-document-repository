import logging
from models.pds_models import Patient, PatientDetails
from requests import Response
from utils.exceptions import (InvalidResourceIdException,
                              PatientNotFoundException, PdsErrorException)


class PatientSearch:
    def fetch_patient_details(
        self,
        nhs_number: str,
    ) -> PatientDetails:
        response = self.pds_request(nhs_number, retry_on_expired=True)
        return self.handle_response(response, nhs_number)

    def handle_response(self, response: Response, nhs_number: str) -> PatientDetails:
        if response.status_code == 200:
            patient = Patient.model_validate(response.json())
            patient_details = patient.get_patient_details(nhs_number)
            return patient_details

        if response.status_code == 404:
            raise PatientNotFoundException(
                "Patient does not exist for given NHS number"
            )

        if response.status_code == 400:
            raise InvalidResourceIdException("Invalid NHS number")

        raise PdsErrorException("Error when requesting patient from PDS")

    def pds_request(self, nhs_number: str, *args, **kwargs) -> Response:
        pass
