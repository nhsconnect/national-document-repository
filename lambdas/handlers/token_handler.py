import json
import logging
import os
import time
import uuid

import boto3
import jwt
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from models.oidc_models import IdTokenClaimSet
from services.dynamo_service import DynamoDBService
from services.ods_api_service_for_password import OdsApiServiceForPassword
from services.ods_api_service_for_smartcard import OdsApiServiceForSmartcard
from services.oidc_service_for_password import OidcServiceForPassword
from services.oidc_service_for_smartcard import OidcServiceForSmartcard
from services.token_handler_ssm_service import TokenHandlerSSMService

from utils.exceptions import AuthorisationException, OrganisationNotFoundException
from utils.lambda_response import ApiGatewayResponse

from enums.permitted_smart_role import PermittedSmartRole
from enums.permitted_role import PermittedRole
from enums.repository_role import RepositoryRole

logger = logging.getLogger()
logger.setLevel(logging.INFO)

token_handler_ssm_service = TokenHandlerSSMService()


def lambda_handler(event, context):
    if is_dev_environment():
        oidc_service = OidcServiceForPassword()
        ods_api_service = OdsApiServiceForPassword()
    else:
        oidc_service = OidcServiceForSmartcard()
        ods_api_service = OdsApiServiceForSmartcard()
    try:
        return token_request(oidc_service, ods_api_service, event)
    except Exception as e:
        return ApiGatewayResponse(500, e, "GET")


def token_request(oidc_service, ods_api_service, event):
    try:
        auth_code = event["queryStringParameters"]["code"]
        state = event["queryStringParameters"]["state"]
        if not (auth_code and state):
            return response_400_bad_request_for_missing_parameter()
    except (KeyError, TypeError):
        return response_400_bad_request_for_missing_parameter()

    try:
        if not have_matching_state_value_in_record(state):
            return ApiGatewayResponse(
                400,
                f"Mismatching state values. Cannot find state {state} in record",
                "GET",
            ).create_api_gateway_response()

        logger.info("Fetching access token from OIDC Provider")
        access_token, id_token_claim_set = oidc_service.fetch_tokens(auth_code)
        logger.info(f"id_token_claim_set:  {id_token_claim_set}")

        logger.info(f"Access token: {access_token}")

        logger.info("Use the access token to fetch user's organisation codes")
        org_ods_codes = oidc_service.fetch_user_org_codes(access_token, id_token_claim_set)
        smartcard_role_code = oidc_service.fetch_user_role_code(access_token, id_token_claim_set, "R")

        permitted_orgs_details = ods_api_service.fetch_organisation_with_permitted_role(org_ods_codes)
        
        logger.info(f"permitted_orgs_details: {permitted_orgs_details}")
        logger.info(f"permitted_orgs_details keys: {permitted_orgs_details.keys()}")

        if len(permitted_orgs_details.keys()) == 0:
            logger.info("User has no org to log in with")
            raise AuthorisationException(f"{permitted_orgs_details.keys()} valid organisations for user")

        session_id = create_login_session(id_token_claim_set)

        logger.info("Creating Repository Role")
        repository_role = generate_repository_role(permitted_orgs_details, smartcard_role_code)

        authorisation_token = issue_auth_token(
            session_id, id_token_claim_set, 
            permitted_orgs_details, 
            smartcard_role_code, repository_role.value
        )

        response = {
            "role" : repository_role.value,
            "authorisation_token": authorisation_token,
        }

        return ApiGatewayResponse(
            200, json.dumps(response), "GET"
        ).create_api_gateway_response()

    except AuthorisationException as error:
        logger.error(error)
        return ApiGatewayResponse(
            401, "Failed to authenticate user with OIDC service", "GET"
        ).create_api_gateway_response()
    except (ClientError, KeyError, TypeError) as error:
        logger.error(error)
        return ApiGatewayResponse(
            500, "Server error", "GET"
        ).create_api_gateway_response()
    except jwt.PyJWTError as error:
        logger.info(f"error while encoding JWT: {error}")
        return ApiGatewayResponse(
            500, "Server error", "GET"
        ).create_api_gateway_response()
    except OrganisationNotFoundException as error:
        logger.info(f"Organisation does not exist for given ODS code: {error}")
        return ApiGatewayResponse(
            500, "Organisation does not exist for given ODS code", "GET"
        ).create_api_gateway_response()


def generate_repository_role(organisation: dict, smartcart_role: str):

    logger.info(f"Smartcard role: {smartcart_role}")
    logger.info(f"PermittedSmartRole.GP_ADMINrole: {PermittedSmartRole.GP_ADMIN.value}")
    logger.info(f"PermittedSmartRole.GP_CLINICAL: {PermittedSmartRole.GP_CLINICAL.name}")
    logger.info(f"PermittedSmartRole.PCSE: {PermittedSmartRole.PCSE.name}")

    
    match smartcart_role:
        case PermittedSmartRole.GP_ADMIN.value:
            logger.info("GP Admin: smartcard ODS identified")
            if has_role_org_ods_code(organisation, token_handler_ssm_service.get_org_role_codes()[0]):
                return RepositoryRole.GP_ADMIN
            return RepositoryRole.NONE
        case PermittedSmartRole.GP_CLINICAL.value:
            logger.info("GP Clinical: smartcard ODS identified")
            if has_role_org_ods_code(organisation, token_handler_ssm_service.get_org_role_codes()[0]):
                return RepositoryRole.GP_CLINICAL
            return RepositoryRole.NONE
        case PermittedSmartRole.PCSE.value:
            logger.info("PCSE: smartcard ODS identified")
            if has_role_org_ods_code(organisation, token_handler_ssm_service.get_org_ods_codes()[0]):
                return RepositoryRole.PCSE
            return RepositoryRole.NONE
        case _:
            logger.info("Role: No smartcard role found")
            return RepositoryRole.NONE


def has_role_org_ods_code(organisation: dict, ods_code: str) -> bool:
    value = organisation["role_code"]
    logger.info(f"ODS IS: {value.upper()}")
    logger.info(f"ODS Check: {ods_code.upper()}")

    if organisation["role_code"].upper() == ods_code.upper():
        return True;
    return False;


# TODO AKH Dynamo Service class
def have_matching_state_value_in_record(state: str) -> bool:
    state_table_name = os.environ["AUTH_STATE_TABLE_NAME"]

    db_service = DynamoDBService()
    query_response = db_service.simple_query(
        table_name=state_table_name, key_condition_expression=Key("State").eq(state)
    )
    return "Count" in query_response and query_response["Count"] > 0


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
    permitted_orgs_and_roles: list[dict],
    smart_card_role: str,
    repository_role : RepositoryRole
) -> str:

    ssm_client = boto3.client("ssm")
    logger.info("starting ssm request to retrieve NDR private key")
    ssm_response = ssm_client.get_parameter(
        Name="jwt_token_private_key", WithDecryption=True
    )
    logger.info("ending ssm request")

    private_key = ssm_response["Parameter"]["Value"]

    thirty_minutes_later = time.time() + (60 * 30)
    ndr_token_expiry_time = min(thirty_minutes_later, id_token_claim_set.exp)

    ndr_token_content = {
        "exp": ndr_token_expiry_time,
        "iss": "nhs repo",
        "smart_card_role": smart_card_role,
        "organisations": permitted_orgs_and_roles,
        "repository_role": str(repository_role),
        "ndr_session_id": session_id,
    }

    logger.info(f"session_id: {session_id}")
    logger.info(f"permitted_orgs_and_roles: {permitted_orgs_and_roles}")
    logger.info(f"id_token_claim_set: {id_token_claim_set}")
    logger.info(f"ndr_token_content: {ndr_token_content}")
    logger.info(f"smartcard_role: {smart_card_role}")
    logger.info(f"repository_role: {str(repository_role)}")

    try:
        authorisation_token = jwt.encode(
            ndr_token_content, private_key, algorithm="RS256"
        )
    except Exception as e:
        logger.info(e)
        raise e

    logger.info(f"encoded JWT: {authorisation_token}")
    return authorisation_token


def response_400_bad_request_for_missing_parameter():
    return ApiGatewayResponse(
        400, "Please supply an authorisation code and state", "GET"
    ).create_api_gateway_response()


# TODO AKH Utility method
# Quick and dirty check to see if we're on Dev
def is_dev_environment() -> bool:
    return False  # "dev" in os.environ["WORKSPACE"] or "ndr" in os.environ["WORKSPACE"]
