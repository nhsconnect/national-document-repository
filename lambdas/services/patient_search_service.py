import logging

from botocore.exceptions import ClientError

from models.pds_models import PatientDetails, Patient
from requests import Response

from utils.exceptions import PdsErrorException, PatientNotFoundException, InvalidResourceIdException

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class PatientSearch:

    def fetch_patient_details(
            self,
            nhs_number: str,
    ) -> PatientDetails:
        try:
            response = self.pds_request(nhs_number, retry_on_expired=True)
            return self.handle_response(response, nhs_number)
        except ClientError as e:
            logger.error(f"Error when getting ssm parameters {e}")
            raise PdsErrorException("Failed to preform patient search")

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

    def pds_request(self, nhsNumber: str, *args, **kwargs):
        pass
