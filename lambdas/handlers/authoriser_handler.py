"""
This code has been modified from AWS blueprint. Below is the original license:

Copyright 2015-2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
Licensed under the Apache License, Version 2.0 (the "License").
You may not use this file except in compliance with the License. A copy of the License is located at
     http://aws.amazon.com/apache2.0/
or in the "license" file accompanying this file.
This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import logging
import os
import time
import json
import boto3
import botocore.exceptions
import jwt
from boto3.dynamodb.conditions import Key
from enums.permitted_role import PermittedRole
from models.auth_policy import AuthPolicy, HttpVerb
from services.dynamo_service import DynamoDBService
from utils.exceptions import AuthorisationException

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    try:
        ssm_public_key_parameter_name = os.environ["SSM_PARAM_JWT_TOKEN_PUBLIC_KEY"]
        logger.info(event)
        client = boto3.client("ssm")
        ssm_response = client.get_parameter(
            Name=ssm_public_key_parameter_name, WithDecryption=True
        )
        public_key = ssm_response["Parameter"]["Value"]

        decoded = jwt.decode(
            event["authorizationToken"], public_key, algorithms=["RS256"]
        )

        ndr_session_id = decoded["ndr_session_id"]

        current_session = find_login_session(ndr_session_id)
        validate_login_session(current_session, ndr_session_id)

    except AuthorisationException as e:
        logger.error(e)
        logger.error("failed to authenticate user")
        return deny_all_response(event)
    except jwt.PyJWTError as e:
        logger.error(f"error while decoding JWT: {e}")
        return deny_all_response(event)
    except (botocore.exceptions.ClientError, KeyError, IndexError) as e:
        logger.error(e)
        return deny_all_response(event)

    principal_id = ""
    _, _, _, region, aws_account_id, api_gateway_arn = event["methodArn"].split(":")
    api_id, stage, _http_verb, _resource_name = api_gateway_arn.split("/")
    user_roles = [org["role"] for org in decoded["organisations"]]
    policy = AuthPolicy(principal_id, aws_account_id)
    policy.restApiId = api_id
    policy.region = region
    policy.stage = stage

    path = "/" + _resource_name
    is_valid_access = validate_access_policy(path, _http_verb, user_roles)
    if is_valid_access:
        set_access_policy(_http_verb, path, user_roles, policy)
    else:
        policy.denyMethod(_http_verb, _resource_name)
    auth_response = policy.build()

    return auth_response


def validate_access_policy(http_verb, path, user_roles):
    logger.info("resource name: %s, http: %s" % (path, http_verb))
    match path:
        case "/DocumentDelete":
            allow_resource = ((PermittedRole.GP_CLINICAL.name in user_roles
                               and http_verb == HttpVerb.DELETE)
                              is False)

        case "/DocumentManifest":
            allow_resource = ((PermittedRole.GP_CLINICAL.name in user_roles
                               and http_verb == HttpVerb.DELETE)
                              is False)

        case "/DocumentReference":
            allow_resource = ((PermittedRole.GP_CLINICAL.name in user_roles
                               and http_verb == HttpVerb.POST)
                              is False)
        case "/SearchDocumentReferences":
            allow_resource = ((PermittedRole.PCSE.name in user_roles
                               and http_verb == HttpVerb.GET)
                              is False)
        case _:
            allow_resource = True

    logger.info("allow resource: %s" % allow_resource)

    return bool(allow_resource)


def set_access_policy(http_verb, path, user_roles, policy):
    if (
            PermittedRole.DEV.name in user_roles
            or PermittedRole.GP_ADMIN.name in user_roles
            or PermittedRole.GP_CLINICAL.name in user_roles
            or PermittedRole.PCSE.name in user_roles
    ):
        policy.allowMethod(http_verb, path)
    else:
        policy.denyMethod(http_verb, path)


def deny_all_response(event):
    _, _, _, region, aws_account_id, api_gateway_arn = event["methodArn"].split(":")
    api_id, stage, http_verb, resource_name = api_gateway_arn.split("/")

    policy = AuthPolicy("", aws_account_id)
    policy.restApiId = api_id
    policy.region = region
    policy.stage = stage
    policy.denyAllMethods()

    auth_response = policy.build()

    return auth_response


def redact_id(session_id: str) -> str:
    # Extract the last 4 chars of session id for logging, as it was in ARF
    return session_id[-4:]


def find_login_session(ndr_session_id):
    logger.debug(
        f"Retrieving session for session ID ending in: f{redact_id(ndr_session_id)}"
    )
    session_table_name = os.environ["AUTH_SESSION_TABLE_NAME"]
    db_service = DynamoDBService()
    query_response = db_service.simple_query(
        table_name=session_table_name,
        key_condition_expression=Key("NDRSessionId").eq(ndr_session_id),
    )

    try:
        current_session = query_response["Items"][0]
        return current_session
    except (KeyError, IndexError) as error:
        logger.info(error)
        raise AuthorisationException(
            f"Unable to find session for session ID ending in: {redact_id(ndr_session_id)}"
        )


def validate_login_session(current_session, ndr_session_id):
    expiry_time = current_session["TimeToExist"]
    time_now = time.time()
    if expiry_time <= time_now:
        raise AuthorisationException(
            f"The session is already expired for session ID ending in: {redact_id(ndr_session_id)}"
        )
