import json
import os
import time
import uuid

import jwt
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from enums.logging_app_interaction import LoggingAppInteraction
from enums.repository_role import RepositoryRole
from models.oidc_models import IdTokenClaimSet
from services.dynamo_service import DynamoDBService
from services.ods_api_service import OdsApiService
from services.oidc_service import OidcService
from services.token_handler_ssm_service import TokenHandlerSSMService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.exceptions import (AuthorisationException,
                              OrganisationNotFoundException,
                              TooManyOrgsException)
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = LoggingService(__name__)

token_handler_ssm_service = TokenHandlerSSMService()


@set_request_context_for_logging
@override_error_check
@ensure_environment_variables(
    names=["AUTH_STATE_TABLE_NAME", "AUTH_SESSION_TABLE_NAME"]
)
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.LOGIN.value

    oidc_service = OidcService()
    ods_api_service = OdsApiService()

    try:
        auth_code = event["queryStringParameters"]["code"]
        state = event["queryStringParameters"]["state"]
        if not (auth_code and state):
            return response_400_bad_request_for_missing_parameter()
    except (KeyError, TypeError):
        return response_400_bad_request_for_missing_parameter()

    try:
        if not have_matching_state_value_in_record(state):
            logger.info(f"Mismatching state values. Cannot find state {state} in record")
            return ApiGatewayResponse(
                400,
                "Failed to authenticate user",
                "GET",
            ).create_api_gateway_response()

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

        logger.info("Creating response")
        response = {
            "role": repository_role.value,
            "authorisation_token": authorisation_token,
        }

        logger.audit_splunk_info(
            "User logged in successfully", {"Result": "Successful login"}
        )
        return ApiGatewayResponse(
            200, json.dumps(response), "GET"
        ).create_api_gateway_response()

    except AuthorisationException as error:
        logger.error(error, {"Result": "Unauthorised"})
        return ApiGatewayResponse(
            401, "Failed to authenticate user with OIDC service", "GET"
        ).create_api_gateway_response()
    except (ClientError, KeyError, TypeError) as error:
        logger.error(error, {"Result": "Unauthorised"})
        return ApiGatewayResponse(
            500, "Server error", "GET"
        ).create_api_gateway_response()
    except jwt.PyJWTError as error:
        logger.info(f"error while encoding JWT: {error}", {"Result": "Unauthorised"})
        return ApiGatewayResponse(
            500, "Server error", "GET"
        ).create_api_gateway_response()
    except OrganisationNotFoundException as error:
        logger.info(
            f"Organisation does not exist for given ODS code: {error}",
            {"Result": "Unauthorised"},
        )
        return ApiGatewayResponse(
            500, "Organisation does not exist for given ODS code", "GET"
        ).create_api_gateway_response()
    except TooManyOrgsException:
        return ApiGatewayResponse(
            500, "No single organisation found for given ods codes", "GET"
        ).create_api_gateway_response()


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


# TODO AKH Dynamo Service class
def have_matching_state_value_in_record(state: str) -> bool:
    state_table_name = os.environ["AUTH_STATE_TABLE_NAME"]

    db_service = DynamoDBService()
    query_response = db_service.simple_query(
        table_name=state_table_name, key_condition_expression=Key("State").eq(state)
    )

    return "Count" in query_response and query_response["Count"] == 1


def remove_used_state(state):
    state_table_name = os.environ["AUTH_STATE_TABLE_NAME"]
    db_service = DynamoDBService()
    deletion_key = {"State": state}
    db_service.delete_item(table_name=state_table_name, key=deletion_key)


# TODO AKH Dynamo Service class
def create_login_session(id_token_claim_set: IdTokenClaimSet) -> str:
    session_table_name = os.environ["AUTH_SESSION_TABLE_NAME"]

    session_id = str(uuid.uuid4())
    session_record = {
        "NDRSessionId": session_id,
        "sid": id_token_claim_set.sid,
        "Subject": id_token_claim_set.sub,
        "TimeToExist": id_token_claim_set.exp,
    }

    dynamodb_service = DynamoDBService()
    dynamodb_service.create_item(table_name=session_table_name, item=session_record)

    return session_id


# TODO AKH SSM service
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

    try:
        authorisation_token = jwt.encode(
            ndr_token_content, private_key, algorithm="RS256"
        )
    except Exception:
        raise AuthorisationException("Unable to create authorisation token")

    logger.info(f"encoded JWT: {authorisation_token}")
    return authorisation_token


def response_400_bad_request_for_missing_parameter():
    return ApiGatewayResponse(
        400, "Please supply an authorisation code and state", "GET"
    ).create_api_gateway_response()
