from enums.repository_role import RepositoryRole
from pydantic import ValidationError
from pydantic_core import PydanticSerializationError
from services.base.ssm_service import SSMService
from utils.audit_logging_setup import LoggingService
from utils.error_response import LambdaError
from utils.exceptions import (
    InvalidResourceIdException,
    PatientNotFoundException,
    PdsErrorException,
    UserNotAuthorisedException,
)
from utils.lambda_exceptions import SearchPatientException
from utils.utilities import get_pds_service

logger = LoggingService(__name__)


class SearchPatientDetailsService:
    def __init__(self, user_role, user_ods_code):
        self.user_role = user_role
        self.user_ods_code = user_ods_code
        self.ssm_service = SSMService()

    def handle_search_patient_request(self, nhs_number):
        try:
            pds_api_service = get_pds_service()(self.ssm_service)
            patient_details = pds_api_service.fetch_patient_details(nhs_number)

            self.check_if_user_authorise(gp_ods=patient_details.general_practice_ods)

            logger.audit_splunk_info(
                "Searched for patient details", {"Result": "Patient found"}
            )
            response = patient_details.model_dump_json(by_alias=True)
            return response
        except PatientNotFoundException as e:
            logger.error(
                f"PDS not found: {str(e)}",
                {"Result": "Patient not found"},
            )
            raise SearchPatientException(404, LambdaError.SearchPatientNoPDS)

        except UserNotAuthorisedException:
            logger.error(
                "PDS Error: User not authorised",
                {"Result": "Patient found, User not authorised to view patient"},
            )
            raise SearchPatientException(404, LambdaError.SearchPatientNoAuth)

        except (InvalidResourceIdException, PdsErrorException) as e:
            logger.error(f"PDS Error: {str(e)}", {"Result": "Patient not found"})
            raise SearchPatientException(400, LambdaError.SearchPatientNoId)

        except (ValidationError, PydanticSerializationError) as e:
            logger.error(
                f"Failed to parse PDS data:{str(e)}", {"Result": "Patient not found"}
            )
            raise SearchPatientException(400, LambdaError.SearchPatientNoParse)

    def check_if_user_authorise(self, gp_ods):
        match self.user_role:
            case RepositoryRole.GP_ADMIN.value:
                # If the GP Admin ods code is null then the patient is not registered.
                # The patient must be registered and registered to the users ODS practise
                if gp_ods == "" or gp_ods != self.user_ods_code:
                    raise UserNotAuthorisedException

            case RepositoryRole.GP_CLINICAL.value:
                # If the GP Clinical ods code is null then the patient is not registered.
                # The patient must be registered and registered to the users ODS practise
                if gp_ods == "" or gp_ods != self.user_ods_code:
                    raise UserNotAuthorisedException

            case RepositoryRole.PCSE.value:
                # If there is a GP ODS field then the patient is registered, PCSE users should be denied access
                if gp_ods != "":
                    raise UserNotAuthorisedException

            case _:
                raise UserNotAuthorisedException
