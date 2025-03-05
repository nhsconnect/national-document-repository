import os

from enums.lambda_error import LambdaError
from enums.repository_role import RepositoryRole
from pydantic import ValidationError
from pydantic_core import PydanticSerializationError
from services.authoriser_service import AuthoriserService
from services.base.dynamo_service import DynamoDBService
from services.base.ssm_service import SSMService
from utils.audit_logging_setup import LoggingService
from utils.exceptions import (
    InvalidResourceIdException,
    PatientNotFoundException,
    PdsErrorException,
    UserNotAuthorisedException,
)
from utils.lambda_exceptions import SearchPatientException
from utils.ods_utils import is_ods_code_active
from utils.request_context import request_context
from utils.utilities import get_pds_service

logger = LoggingService(__name__)


class SearchPatientDetailsService:
    def __init__(self, user_role, user_ods_code):
        self.user_role = user_role
        self.user_ods_code = user_ods_code
        self.ssm_service = SSMService()
        self.db_service = DynamoDBService()
        self.auth_service = AuthoriserService()
        self.session_table_name = os.getenv("AUTH_SESSION_TABLE_NAME")
        self.permitted_field = "AllowedNHSNumbers"
        self.deceased_field = "DeceasedNHSNumbers"

    def handle_search_patient_request(self, nhs_number):
        try:
            pds_service = get_pds_service()
            patient_details = pds_service.fetch_patient_details(nhs_number)
            if not patient_details.deceased:
                self.check_if_user_authorise(
                    gp_ods_for_patient=patient_details.general_practice_ods
                )

            logger.audit_splunk_info(
                "Searched for patient details", {"Result": "Patient found"}
            )

            self.update_auth_session_with_permitted_search(
                nhs_number=nhs_number, deceased=patient_details.deceased
            )

            response = patient_details.model_dump_json(
                by_alias=True,
                exclude={
                    "death_notification_status",
                    "general_practice_ods",
                },
            )
            return response
        except PatientNotFoundException as e:
            logger.error(
                f"{LambdaError.SearchPatientNoPDS.to_str()}: {str(e)}",
                {"Result": "Patient not found"},
            )
            raise SearchPatientException(404, LambdaError.SearchPatientNoPDS)

        except UserNotAuthorisedException as e:
            logger.error(
                f"{LambdaError.SearchPatientNoAuth.to_str()}: {str(e)}",
                {"Result": "Patient found, User not authorised to view patient"},
            )
            raise SearchPatientException(404, LambdaError.SearchPatientNoAuth)

        except (InvalidResourceIdException, PdsErrorException) as e:
            logger.error(
                f"{LambdaError.SearchPatientNoId.to_str()}: {str(e)}",
                {"Result": "Patient not found"},
            )
            raise SearchPatientException(400, LambdaError.SearchPatientNoId)

        except (ValidationError, PydanticSerializationError) as e:
            logger.error(
                f"{LambdaError.SearchPatientNoParse.to_str()}: {str(e)}",
                {"Result": "Patient not found"},
            )
            raise SearchPatientException(400, LambdaError.SearchPatientNoParse)

    def check_if_user_authorise(self, gp_ods_for_patient):
        patient_is_active = is_ods_code_active(gp_ods_for_patient)
        match self.user_role:
            case RepositoryRole.GP_ADMIN.value:
                # Not raising error here if gp_ods is null / empty
                if patient_is_active and gp_ods_for_patient != self.user_ods_code:
                    raise UserNotAuthorisedException

            case RepositoryRole.GP_CLINICAL.value:
                # If the GP Clinical ods code is null then the patient is not registered.
                # The patient must be registered and registered to the users ODS practise
                if not patient_is_active or gp_ods_for_patient != self.user_ods_code:
                    raise UserNotAuthorisedException

            case RepositoryRole.PCSE.value:
                # If there is a GP ODS field then the patient is registered, PCSE users should be denied access
                if patient_is_active:
                    raise UserNotAuthorisedException

            case _:
                raise UserNotAuthorisedException

    def update_auth_session_with_permitted_search(
        self, nhs_number: str, deceased: bool
    ):
        ndr_session_id = request_context.authorization.get("ndr_session_id")
        current_session = self.auth_service.find_login_session(ndr_session_id)
        allowed_nhs_numbers = self.auth_service.allowed_nhs_numbers
        deceased_nhs_numbers = current_session.get(self.deceased_field, False)
        logger.info("Searching Auth session table for existing NHS number")
        if nhs_number in allowed_nhs_numbers:
            logger.info(
                "Permitted search, NHS number already exists in allowed NHS numbers"
            )
            return

        if deceased:
            self.update_auth_session_table_with_new_nhs_number(
                field_name=self.deceased_field,
                nhs_number=nhs_number,
                existing_nhs_numbers=deceased_nhs_numbers,
                ndr_session_id=ndr_session_id,
            )
        if not deceased or self.user_role == RepositoryRole.PCSE.value:
            self.update_auth_session_table_with_new_nhs_number(
                field_name=self.permitted_field,
                nhs_number=nhs_number,
                existing_nhs_numbers=allowed_nhs_numbers,
                ndr_session_id=ndr_session_id,
            )
        logger.info("Permitted search, NHS number will be added")

    def update_auth_session_table_with_new_nhs_number(
        self,
        field_name: str,
        nhs_number: str,
        existing_nhs_numbers: list,
        ndr_session_id: str,
    ):
        updated_fields = self.create_updated_permitted_search_fields(
            field_name=field_name,
            nhs_number=nhs_number,
            existing_nhs_numbers=existing_nhs_numbers,
        )

        self.db_service.update_item(
            table_name=self.session_table_name,
            key_pair={"NDRSessionId": ndr_session_id},
            updated_fields=updated_fields,
            condition_expression=(
                f"attribute_not_exists({field_name})"
                if not existing_nhs_numbers
                else None
            ),
        )

    def create_updated_permitted_search_fields(
        self, field_name, nhs_number: str, existing_nhs_numbers: list[str]
    ) -> dict[str, str]:
        if existing_nhs_numbers:
            existing_nhs_numbers.append(nhs_number)
            existing_nhs_numbers_str = ",".join(existing_nhs_numbers)
            updated_fields = {field_name: existing_nhs_numbers_str}

        else:
            updated_fields = {field_name: nhs_number}

        return updated_fields
