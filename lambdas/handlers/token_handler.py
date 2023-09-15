import json
import logging
import os
import time
import uuid

import boto3
import botocore.exceptions
import jwt
from boto3.dynamodb.conditions import Key

# from services.dynamo_services import DynamoDBService
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
    except KeyError:
        return ApiGatewayResponse(
            400, "Please supply an authorisation code and state", "GET"
        ).create_api_gateway_response()

    try:
        # TODO: after merging with other branch, refactor dynamo db service to allow query with only P-Key
        # Right now the implementation in this branch doesn't allow us to query without other field names
        state_table_name = os.environ["AUTH_STATE_TABLE_NAME"]
        temp_dynamo_resource = boto3.resource("dynamodb")
        state_table = temp_dynamo_resource.Table(state_table_name)
        query_response = state_table.query(
            KeyConditionExpression=Key("State").eq(state)
        )

        if "Count" not in query_response or query_response["Count"] == 0:
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
        if len(permitted_orgs_and_roles) == 0:
            logger.info("User has no valid organisations to log in")
            raise AuthorisationException("No valid organisations for user")

        session_table_name = os.environ["AUTH_SESSION_TABLE_NAME"]

        # TODO: switch to use the DynamoDBService from other branch once we merge
        # session_table_dynamo_service = DynamoDBService(table_name=session_table_name)

        session_table = temp_dynamo_resource.Table(session_table_name)

        session_id = str(uuid.uuid4())
        session_record = {
            "NDRSessionId": session_id,
            "sid": id_token_claim_set.sid,
            "Subject": id_token_claim_set.sub,
            "TimeToExist": id_token_claim_set.exp,
        }
        session_table.put_item(Item=session_record)
        # session_table_dynamo_service.post_item_service(item=session_record)

        # issue Authorisation token
        ssm_client = boto3.client("ssm")

        logger.info("starting ssm request to retrieve NDR private key")
        ssm_response = ssm_client.get_parameter(
            Name="jwt_token_private_key", WithDecryption=True
        )
        logger.info("ending ssm request")
        private_key = ssm_response["Parameter"]["Value"]

        ndr_token_content = {
            "exp": min(time.time() + 60 * 30, id_token_claim_set.exp),
            "iss": "nhs repo",
            "organisations": permitted_orgs_and_roles,
            "ndr_session_id": session_id,
        }

        authorisation_token = jwt.encode(
            ndr_token_content, private_key, algorithm="RS256"
        )
        logger.info(f"encoded JWT: {authorisation_token}")

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
        return ApiGatewayResponse(500, "Server error", "GET").create_api_gateway_response()
    except jwt.PyJWTError as error:
        logger.info(f"error while encoding JWT: {error}")
        return ApiGatewayResponse(500, "Server error", "GET").create_api_gateway_response()

    return ApiGatewayResponse(
        200, json.dumps(response), "GET"
    ).create_api_gateway_response()
