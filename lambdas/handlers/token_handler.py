import json
import logging
import os
import time
import uuid

import boto3
import botocore.exceptions
import jwt
from boto3.dynamodb.conditions import Key
from models.oidc_models import IdTokenClaimSet
from services.dynamo_service import DynamoDBService
from services.ods_api_service import OdsApiService
from services.oidc_service import OidcService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.exceptions import AuthorisationException, OdsErrorException
from utils.lambda_response import ApiGatewayResponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# TODO Move this to SSM
PCSE_ODS_CODE_TO_BE_PUT_IN_PARAM_STORE = "X4S4L"


@ensure_environment_variables(
    [
        "OIDC_CALLBACK_URL"
    ]
)
def lambda_handler(event, _context):
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

        oidc_service = OidcService()

        logger.info("Fetching access token from OIDC Provider")
        access_token, id_token_claim_set = oidc_service.fetch_tokens(auth_code)

        # get selected_roleid from id_token_claimset
        selected_roleid = id_token_claim_set.selected_roleid

        logger.info("Use the access token to fetch details of user's selected role")
        ods_code = oidc_service.fetch_users_org_code(access_token, selected_roleid)
        if ods_code is None:
            return ApiGatewayResponse(500, "Unable to fathom user role", "GET")

        is_gpp = OdsApiService.is_gpp_org(ods_code)
        is_pcse = ods_code == PCSE_ODS_CODE_TO_BE_PUT_IN_PARAM_STORE

        if (not (is_gpp or is_pcse)):
            logger.info("User's selected role is not for a GPP or PCSE")
            raise AuthorisationException("Selected role invalid")

        session_id = create_login_session(id_token_claim_set)

        if is_dev_environment():
            permitted_orgs_and_roles = OdsApiService.fetch_organisation_with_permitted_role(
                oidc_service.fetch_users_org_code(access_token)
            )
            authorisation_token = issue_auth_token(
                session_id, id_token_claim_set, permitted_orgs_and_roles
            )
            response = {
                "organisations": permitted_orgs_and_roles,
                "authorisation_token": authorisation_token,
            }
        else:
            response = ""

    except AuthorisationException as error:
        logger.error(error)
        return ApiGatewayResponse(
            401, "Failed to authenticate user with OIDC service", "GET"
        ).create_api_gateway_response()
    except (botocore.exceptions.ClientError, KeyError, TypeError) as error:
        logger.error(error)
        return ApiGatewayResponse(
            500, "Server error", "GET"
        ).create_api_gateway_response()
    except jwt.PyJWTError as error:
        logger.info(f"error while encoding JWT: {error}")
        return ApiGatewayResponse(
            500, "Server error", "GET"
        ).create_api_gateway_response()
    except OdsErrorException:
        return ApiGatewayResponse(
            500, "Failed to fetch organisation data from ODS", "GET"
        ).create_api_gateway_response()

    return ApiGatewayResponse(
        200, json.dumps(response), "GET"
    ).create_api_gateway_response()


def have_matching_state_value_in_record(state: str) -> bool:
    state_table_name = os.environ["AUTH_STATE_TABLE_NAME"]

    db_service = DynamoDBService()
    query_response = db_service.simple_query(
        table_name=state_table_name, key_condition_expression=Key("State").eq(state)
    )
    return "Count" in query_response and query_response["Count"] > 0


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


def issue_auth_token(
        session_id: str,
        id_token_claim_set: IdTokenClaimSet,
        permitted_orgs_and_roles: list[dict],
) -> str:
    ssm_client = boto3.client("ssm")
    logger.info("starting ssm request to retrieve NDR private key")
    ssm_response = ssm_client.get_parameter(
        Name="jwt_token_private_key", WithDecryption=True
    )
    logger.info("ending ssm request")

    private_key = ssm_response["Parameter"]["Value"]

    thirty_minutes_later = time.time() + 60 * 30
    ndr_token_expiry_time = min(thirty_minutes_later, id_token_claim_set.exp)

    ndr_token_content = {
        "exp": ndr_token_expiry_time,
        "iss": "nhs repo",
        "organisations": permitted_orgs_and_roles,
        "ndr_session_id": session_id,
    }
    authorisation_token = jwt.encode(ndr_token_content, private_key, algorithm="RS256")
    logger.info(f"encoded JWT: {authorisation_token}")
    return authorisation_token


def response_400_bad_request_for_missing_parameter():
    return ApiGatewayResponse(
        400, "Please supply an authorisation code and state", "GET"
    ).create_api_gateway_response()

# Quick and dirty check to see if we're on Dev
def is_dev_environment() -> bool:
    return "dev" in os.environ["OIDC_CALLBACK_URL"]
