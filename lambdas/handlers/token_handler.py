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
from utils.exceptions import AuthorisationException
from utils.lambda_response import ApiGatewayResponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)


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

        logger.info("Use the access token to fetch user's organisation codes")
        org_codes = oidc_service.fetch_user_org_codes(access_token)

        permitted_orgs_and_roles = OdsApiService.fetch_organisation_with_permitted_role(
            org_codes
        )
        permitted_orgs_and_roles = [
            permitted_orgs_and_roles
        ]
        if len(permitted_orgs_and_roles) == 0:
            logger.info("User has no valid organisations to log in")
            raise AuthorisationException("No valid organisations for user")

        session_id = create_login_session(id_token_claim_set)

        authorisation_token = issue_auth_token(
            session_id, id_token_claim_set, permitted_orgs_and_roles
        )

        response = {
            "organisations": permitted_orgs_and_roles,
            "authorisation_token": authorisation_token,
        }

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
