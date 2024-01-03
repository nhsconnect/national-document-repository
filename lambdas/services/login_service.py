import os
import time
import uuid

import jwt
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from oauthlib.oauth2 import WebApplicationClient

from enums.repository_role import RepositoryRole
from models.oidc_models import IdTokenClaimSet
from services.dynamo_service import DynamoDBService
from services.ods_api_service import OdsApiService
from services.oidc_service import OidcService
from services.ssm_service import SSMService
from services.token_handler_ssm_service import TokenHandlerSSMService
from utils.audit_logging_setup import LoggingService
from utils.exceptions import (
    LoginException,
    OidcApiException,
    AuthorisationException,
    TooManyOrgsException,
    OdsErrorException,
    OrganisationNotFoundException,
)

logger = LoggingService(__name__)


class LoginService:
    def __init__(self):
        self.db_service = DynamoDBService()
        self.token_handler_ssm_service = TokenHandlerSSMService()
        self.oidc_service = OidcService()
        self.ods_api_service = OdsApiService()

    def generate_session(self, state, auth_code) -> dict:
        logger.info("Login process started")

        try:
            if not self.have_matching_state_value_in_record(state):
                logger.info(
                    f"Mismatching state values. Cannot find state {state} in record"
                )
                raise LoginException(401, "Unrecognised state value")
        except ClientError:
            raise LoginException(500, "Unable to validate state")

        logger.info(
            "Setting up oidc service"
        )

        self.oidc_service.set_up_oidc_parameters(SSMService, WebApplicationClient)

        logger.info("Fetching access token from OIDC Provider")
        try:
            access_token, id_token_claim_set = self.oidc_service.fetch_tokens(auth_code)

            logger.info(
                "Use the access token to fetch user's organisation and smartcard codes"
            )

            org_ods_codes = self.oidc_service.fetch_user_org_codes(
                access_token, id_token_claim_set
            )

            smartcard_role_code, user_id = self.oidc_service.fetch_user_role_code(
                access_token, id_token_claim_set, "R"
            )
        except OidcApiException:
            raise LoginException(500, "Issue when contacting CIS2")
        except AuthorisationException:
            raise LoginException(
                401, "Cannot log user in, expected information from CIS2 is missing"
            )

        try:
            permitted_orgs_details = (
                self.ods_api_service.fetch_organisation_with_permitted_role(
                    org_ods_codes
                )
            )
        except (TooManyOrgsException, OdsErrorException):
            raise LoginException(500, "Bad response from ODS API")
        except OrganisationNotFoundException:
            raise LoginException(401, "No org found for given ODS code")

        logger.info(f"Permitted_orgs_details: {permitted_orgs_details}")

        if len(permitted_orgs_details.keys()) == 0:
            logger.info("User has no org to log in with")
            raise LoginException(
                401, f"{permitted_orgs_details.keys()} valid organisations for user"
            )

        session_id = self.create_login_session(id_token_claim_set)

        logger.info("Calculating repository role")
        repository_role = self.generate_repository_role(
            permitted_orgs_details, smartcard_role_code
        )

        logger.info("Creating authorisation token")
        authorisation_token = self.issue_auth_token(
            session_id,
            id_token_claim_set,
            permitted_orgs_details,
            smartcard_role_code,
            repository_role.value,
            user_id,
        )

        is_bsol = (
            repository_role.value == RepositoryRole.GP_ADMIN.value
            and permitted_orgs_details["is_BSOL"]
        )

        logger.info("Returning authentication details")
        response = {
            "isBSOL": is_bsol,
            "role": repository_role.value,
            "authorisation_token": authorisation_token,
        }
        return response

    def have_matching_state_value_in_record(self, state: str) -> bool:
        state_table_name = os.environ["AUTH_STATE_TABLE_NAME"]

        query_response = self.db_service.simple_query(
            table_name=state_table_name, key_condition_expression=Key("State").eq(state)
        )

        state_match = "Count" in query_response and query_response["Count"] == 1

        if state_match:
            try:
                self.remove_used_state(state)
            except ClientError:
                raise LoginException(500, "Unable to remove used state value")

        return state_match

    def remove_used_state(self, state):
        state_table_name = os.environ["AUTH_STATE_TABLE_NAME"]
        deletion_key = {"State": state}
        self.db_service.delete_item(table_name=state_table_name, key=deletion_key)

    def generate_repository_role(self, organisation: dict, smartcard_role: str):
        logger.info(f"Smartcard Role: {smartcard_role}")

        if (
            self.token_handler_ssm_service.get_smartcard_role_gp_admin()
            == smartcard_role
        ):
            logger.info("GP Admin: smartcard ODS identified")
            if self.has_role_org_role_code(
                organisation, self.token_handler_ssm_service.get_org_role_codes()[0]
            ):
                return RepositoryRole.GP_ADMIN
            return RepositoryRole.NONE

        if (
            self.token_handler_ssm_service.get_smartcard_role_gp_clinical()
            == smartcard_role
        ):
            logger.info("GP Clinical: smartcard ODS identified")
            if self.has_role_org_role_code(
                organisation, self.token_handler_ssm_service.get_org_role_codes()[0]
            ):
                return RepositoryRole.GP_CLINICAL
            return RepositoryRole.NONE

        if self.token_handler_ssm_service.get_smartcard_role_pcse() == smartcard_role:
            logger.info("PCSE: smartcard ODS identified")
            if self.has_role_org_ods_code(
                organisation, self.token_handler_ssm_service.get_org_ods_codes()[0]
            ):
                return RepositoryRole.PCSE
            return RepositoryRole.NONE

        logger.info("Role: No smartcard role found")
        return RepositoryRole.NONE

    @staticmethod
    def has_role_org_role_code(organisation: dict, role_code: str) -> bool:
        if organisation["role_code"].upper() == role_code.upper():
            return True
        return False

    @staticmethod
    def has_role_org_ods_code(organisation: dict, ods_code: str) -> bool:
        if organisation["org_ods_code"].upper() == ods_code.upper():
            return True
        return False

    def issue_auth_token(
        self,
        session_id: str,
        id_token_claim_set: IdTokenClaimSet,
        user_org_details: list[dict],
        smart_card_role: str,
        repository_role: RepositoryRole,
        user_id: str,
    ) -> str:
        private_key = self.token_handler_ssm_service.get_jwt_private_key()

        thirty_minutes_later = time.time() + (60 * 30)
        ndr_token_expiry_time = min(thirty_minutes_later, id_token_claim_set.exp)

        ndr_token_content = {
            "exp": ndr_token_expiry_time,
            "iss": "nhs repo",
            "smart_card_role": smart_card_role,
            "selected_organisation": user_org_details,
            "repository_role": str(repository_role),
            "ndr_session_id": session_id,
            "nhs_user_id": user_id,
        }

        authorisation_token = jwt.encode(
            ndr_token_content, private_key, algorithm="RS256"
        )
        return authorisation_token

    def create_login_session(self, id_token_claim_set: IdTokenClaimSet) -> str:
        session_table_name = os.environ["AUTH_SESSION_TABLE_NAME"]

        session_id = str(uuid.uuid4())
        session_record = {
            "NDRSessionId": session_id,
            "sid": id_token_claim_set.sid,
            "Subject": id_token_claim_set.sub,
            "TimeToExist": id_token_claim_set.exp,
        }

        self.db_service.create_item(table_name=session_table_name, item=session_record)

        return session_id
