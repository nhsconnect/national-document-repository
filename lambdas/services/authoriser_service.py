import os
import time

from enums.repository_role import RepositoryRole
from services.base.dynamo_service import DynamoDBService
from services.token_service import TokenService
from utils.audit_logging_setup import LoggingService
from utils.exceptions import AuthorisationException
from utils.request_context import request_context
from utils.utilities import redact_id_to_last_4_chars

logger = LoggingService(__name__)

token_service = TokenService()


class AuthoriserService:
    def __init__(self):
        self.redact_session_id = ""
        self.allowed_nhs_numbers = []

    def auth_request(
        self, path, ssm_jwt_public_key_parameter, auth_token, nhs_number: str = None
    ):
        try:
            decoded_token = token_service.get_public_key_and_decode_auth_token(
                auth_token=auth_token,
                ssm_public_key_parameter=ssm_jwt_public_key_parameter,
            )
            if decoded_token is None:
                raise AuthorisationException("Error while decoding JWT")
            request_context.authorization = decoded_token

            ndr_session_id = decoded_token.get("ndr_session_id")
            self.redact_session_id = redact_id_to_last_4_chars(ndr_session_id)
            user_role = decoded_token.get("repository_role")

            current_session = self.find_login_session(ndr_session_id)
            self.validate_login_session(float(current_session["TimeToExist"]))

            resource_denied = self.deny_access_policy(path, user_role, nhs_number)

            allow_policy = False

            if not resource_denied:
                accepted_roles = RepositoryRole.list()
                if user_role in accepted_roles:
                    allow_policy = True
            return allow_policy

        except (KeyError, IndexError) as e:
            raise AuthorisationException(e)

    def deny_access_policy(self, path, user_role, nhs_number: str = None):
        logger.info(f"Path: {path}")
        deny_access_to_patient = (
            nhs_number not in self.allowed_nhs_numbers if nhs_number else False
        )
        deny_access_to_clinical_role = user_role == RepositoryRole.GP_CLINICAL.value
        match path:
            case "/DocumentDelete":
                deny_resource = deny_access_to_patient or deny_access_to_clinical_role

            case "/DocumentManifest":
                deny_resource = deny_access_to_patient or deny_access_to_clinical_role

            case "/DocumentReference":
                deny_resource = deny_access_to_patient or deny_access_to_clinical_role

            case "/SearchPatient":
                deny_resource = False

            case _:
                deny_resource = deny_access_to_patient

        logger.info("Allow resource: %s" % (not deny_resource))

        return bool(deny_resource)

    def find_login_session(self, ndr_session_id: str):
        logger.info(
            f"Retrieving session for session ID ending in: f{self.redact_session_id}"
        )
        session_table_name = os.environ["AUTH_SESSION_TABLE_NAME"]
        db_service = DynamoDBService()
        query_response = db_service.query_all_fields(
            table_name=session_table_name,
            search_key="NDRSessionId",
            search_condition=ndr_session_id,
        )

        try:
            current_session = query_response["Items"][0]
            list_of_allowed_nhs_numbers = current_session.get("AllowedNHSNumbers", [])
            if list_of_allowed_nhs_numbers:
                self.allowed_nhs_numbers = list_of_allowed_nhs_numbers.split(",")
            return current_session
        except (KeyError, IndexError):
            raise AuthorisationException(
                f"Unable to find session for session ID ending in: {self.redact_session_id}",
            )

    def validate_login_session(self, session_expiry_time: float):
        time_now = time.time()
        if session_expiry_time <= time_now:
            raise AuthorisationException(
                f"The session is already expired for session ID ending in: {self.redact_session_id}",
            )
