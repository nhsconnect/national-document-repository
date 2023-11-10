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

import os
import time

import botocore.exceptions
import jwt
from boto3.dynamodb.conditions import Key
from enums.repository_role import RepositoryRole
from models.auth_policy import AuthPolicy
from services.dynamo_service import DynamoDBService
from services.ssm_service import SSMService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.exceptions import AuthorisationException

logger = LoggingService(__name__)


@ensure_environment_variables(names=["SSM_PARAM_JWT_TOKEN_PUBLIC_KEY"])
def lambda_handler(event, context):
    try:
        logger.info(event)
        ssm_service = SSMService()
        ssm_public_key_parameter_name = os.environ["SSM_PARAM_JWT_TOKEN_PUBLIC_KEY"]

        public_key = ssm_service.get_ssm_parameter(ssm_public_key_parameter_name, True)

        decoded = jwt.decode(
            event["authorizationToken"], public_key, algorithms=["RS256"]
        )

        ndr_session_id = decoded["ndr_session_id"]

        current_session = find_login_session(ndr_session_id)
        validate_login_session(current_session, ndr_session_id)
        user_role = decoded["repository_role"]

        principal_id = ""
        _, _, _, region, aws_account_id, api_gateway_arn = event["methodArn"].split(":")
        api_id, stage, _http_verb, _resource_name = api_gateway_arn.split("/")

        policy = AuthPolicy(principal_id, aws_account_id)
        policy.restApiId = api_id
        policy.region = region
        policy.stage = stage

        path = "/" + _resource_name
        resource_denied = validate_access_policy(_http_verb, path, user_role)
        if resource_denied:
            policy.denyMethod(_http_verb, path)
        else:
            set_access_policy(_http_verb, path, user_role, policy)
        auth_response = policy.build()

        return auth_response

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


def validate_access_policy(http_verb, path, user_role):
    logger.info("Validating resource req: %s, http: %s" % (path, http_verb))

    logger.info(f"Path: {path}")
    match path:
        case "/DocumentDelete":
            deny_resource = (
                user_role is RepositoryRole.GP_CLINICAL.value
            )

        case "/DocumentManifest":
            deny_resource = (
                user_role == RepositoryRole.GP_CLINICAL.value
            )

        case "/DocumentReference":
            deny_resource = (
                user_role == RepositoryRole.GP_CLINICAL.value
            )

        case _:
            deny_resource = False

    logger.info("Allow resource: %s" % bool(deny_resource) is False)

    return bool(deny_resource)


def set_access_policy(http_verb, path, user_role, policy):
    accepted_roles = tuple(item.value for item in RepositoryRole)
    if user_role in accepted_roles:
        policy.allowMethod(http_verb, path)
    # for now, allow all method for GP and DEV role, and allow only search document for PCSE
    if RepositoryRole.GP_ADMIN.value in user_role:
        policy.allowAllMethods()
    elif RepositoryRole.GP_CLINICAL.value in user_role:
        policy.allowAllMethods()
    elif RepositoryRole.PCSE.value in user_role:
        policy.allowAllMethods()
        # policy.allowMethod(HttpVerb.GET, "/SearchDocumentReferences")
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
    logger.info(
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
