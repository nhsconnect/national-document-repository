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
        public_key = ssm_service.get_ssm_parameter(os.environ["SSM_PARAM_JWT_TOKEN_PUBLIC_KEY"], True)

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
        path = "/" + _resource_name

        policy = AuthPolicy(principal_id, aws_account_id)
        policy.restApiId = api_id
        policy.region = region
        policy.stage = stage

        resource_denied = validate_access_policy(_http_verb, path, user_role)

        if resource_denied:
            policy.denyMethod(_http_verb, path)
        else:
            accepted_roles = RepositoryRole.list()
            if user_role in accepted_roles:
                policy.allowMethod(_http_verb, path)
            else:
                policy.denyMethod(_http_verb, path)

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
    match path:
        case "/DocumentDelete":
            deny_resource = (
                    user_role is RepositoryRole.GP_CLINICAL.value
                    or user_role is RepositoryRole.GP_ADMIN.value
            )

        case "/DocumentManifest":
            deny_resource = (
                    user_role is RepositoryRole.GP_CLINICAL.value
                    or user_role is RepositoryRole.GP_ADMIN.value
            )

        case "/DocumentReference":
            deny_resource = (
                    user_role is RepositoryRole.GP_CLINICAL.value
                    or user_role is RepositoryRole.GP_ADMIN.value
            )

        case "/SearchDocumentReferences":
            deny_resource = user_role is RepositoryRole.PCSE.value

        case _:
            deny_resource = False

    logger.info("Allow resource: %s" % bool(deny_resource) is False)

    return bool(deny_resource)


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
