import boto3
import jwt

from enums.repository_role import RepositoryRole
from handlers.token_handler import (
    have_matching_state_value_in_record,
    remove_used_state,
    create_login_session,
)
from services.ods_api_service import OdsApiService
from services.oidc_service import OidcService
from services.token_handler_ssm_service import TokenHandlerSSMService
from utils.audit_logging_setup import LoggingService
from utils.exceptions import AuthorisationException

logger = LoggingService(__name__)
token_handler_ssm_service = TokenHandlerSSMService()
oidc_service = OidcService()
ods_api_service = OdsApiService()


class LoginService:
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb", region_name="eu-west-2")

    """
    Login paths:
    happy path -> respond with response body (JWT + repo role)
    unhappy path -> respond with error
        Invalid org - auth exception
        Invalid role code - auth exception
        Logical error - 
        
    """
    # TODO review toomanyorgs exception, may not be possible to trigger
    # TODO assign repo role at same time as finding user's role?
    # TODO reduce calls we make to external APIs. Previously there's been a lot of duplicate calls.

    def exchange_token(self, state, auth_code) -> tuple:
        if not have_matching_state_value_in_record(state):
            logger.info(
                f"Mismatching state values. Cannot find state {state} in record"
            )
            return AuthorisationException("Unrecognised state value")

        remove_used_state(state)

        logger.info("Fetching access token from OIDC Provider")
        access_token, id_token_claim_set = oidc_service.fetch_tokens(auth_code)

        logger.info(
            "Use the access token to fetch user's organisation and smartcard codes"
        )
        org_ods_codes = oidc_service.fetch_user_org_codes(
            access_token, id_token_claim_set
        )
        smartcard_role_code, user_id = oidc_service.fetch_user_role_code(
            access_token, id_token_claim_set, "R"
        )
        permitted_orgs_details = ods_api_service.fetch_organisation_with_permitted_role(
            org_ods_codes
        )

        logger.info(f"Permitted_orgs_details: {permitted_orgs_details}")

        if len(permitted_orgs_details.keys()) == 0:
            logger.info("User has no org to log in with")
            raise AuthorisationException(
                f"{permitted_orgs_details.keys()} valid organisations for user"
            )

        session_id = create_login_session(id_token_claim_set)

        logger.info("Calculating repository role")
        repository_role = generate_repository_role(
            permitted_orgs_details, smartcard_role_code
        )

        logger.info("Creating authorisation token")
        authorisation_token = issue_auth_token(
            session_id,
            id_token_claim_set,
            permitted_orgs_details,
            smartcard_role_code,
            repository_role.value,
            user_id,
        )

        logger.info("Returning authentication details")
        return (repository_role.value, authorisation_token)


def generate_repository_role(organisation: dict, smartcart_role: str):
    logger.info(f"Smartcard Role: {smartcart_role}")

    if token_handler_ssm_service.get_smartcard_role_gp_admin() == smartcart_role:
        logger.info("GP Admin: smartcard ODS identified")
        if has_role_org_role_code(
            organisation, token_handler_ssm_service.get_org_role_codes()[0]
        ):
            return RepositoryRole.GP_ADMIN
        return RepositoryRole.NONE

    if token_handler_ssm_service.get_smartcard_role_gp_clinical() == smartcart_role:
        logger.info("GP Clinical: smartcard ODS identified")
        if has_role_org_role_code(
            organisation, token_handler_ssm_service.get_org_role_codes()[0]
        ):
            return RepositoryRole.GP_CLINICAL
        return RepositoryRole.NONE

    if token_handler_ssm_service.get_smartcard_role_pcse() == smartcart_role:
        logger.info("PCSE: smartcard ODS identified")
        if has_role_org_ods_code(
            organisation, token_handler_ssm_service.get_org_ods_codes()[0]
        ):
            return RepositoryRole.PCSE
        return RepositoryRole.NONE

    logger.info("Role: No smartcard role found")
    return RepositoryRole.NONE


def has_role_org_role_code(organisation: dict, role_code: str) -> bool:
    if organisation["role_code"].upper() == role_code.upper():
        return True
    return False


def has_role_org_ods_code(organisation: dict, ods_code: str) -> bool:
    if organisation["org_ods_code"].upper() == ods_code.upper():
        return True
    return False


def issue_auth_token(
    session_id: str,
    id_token_claim_set: IdTokenClaimSet,
    user_org_details: list[dict],
    smart_card_role: str,
    repository_role: RepositoryRole,
    user_id: str,
) -> str:
    private_key = token_handler_ssm_service.get_jwt_private_key()

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

    authorisation_token = jwt.encode(ndr_token_content, private_key, algorithm="RS256")
    return authorisation_token
