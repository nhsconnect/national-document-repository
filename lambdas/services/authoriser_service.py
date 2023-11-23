import os
import time

from boto3.dynamodb.conditions import Key

from enums.repository_role import RepositoryRole
from services.dynamo_service import DynamoDBService
from services.ssm_service import SSMService
from services.token_service import TokenService
from utils.audit_logging_setup import LoggingService
from utils.exceptions import AuthorisationException
from utils.request_context import request_context
from utils.utilities import redact_id_to_last_4_chars

logger = LoggingService(__name__)


class AuthoriserService:
    def __init__(
        self,
        path,
        _http_verb,
    ):
        self.path = path
        self._http_verb = _http_verb
        self.redact_session_id = ""
        self.token_service = TokenService(SSMService())

    def auth_request(self, ssm_jwt_public_key_parameter, auth_token):
        try:
            decoded_token = self.token_service.get_public_key_and_decode_auth_token(
                auth_token=auth_token,
                ssm_public_key_parameter=ssm_jwt_public_key_parameter,
            )
            if decoded_token is None:
                raise AuthorisationException("error while decoding JWT")
            request_context.authorization = decoded_token

            ndr_session_id = decoded_token.get("ndr_session_id")
            self.redact_session_id = redact_id_to_last_4_chars(ndr_session_id)
            user_role = decoded_token.get("repository_role")

            current_session = self.find_login_session(ndr_session_id)
            self.validate_login_session(float(current_session["TimeToExist"]))

            resource_denied = self.deny_access_policy(user_role)
            allow_policy = False

            if not resource_denied:
                accepted_roles = RepositoryRole.list()
                if user_role in accepted_roles:
                    allow_policy = True
            return allow_policy

        except (KeyError, IndexError) as e:
            raise AuthorisationException(e)

    def deny_access_policy(self, user_role):
        logger.info(
            "Validating resource req: %s, http: %s" % (self.path, self._http_verb)
        )

        logger.info(f"Path: {self.path}")
        match self.path:
            case "/DocumentDelete":
                deny_resource = user_role == RepositoryRole.GP_CLINICAL.value

            case "/DocumentManifest":
                deny_resource = user_role == RepositoryRole.GP_CLINICAL.value

            case "/DocumentReference":
                deny_resource = user_role == RepositoryRole.GP_CLINICAL.value

            case _:
                deny_resource = False

        logger.info("Allow resource: %s" %(not deny_resource))

        return bool(deny_resource)

    def find_login_session(self, ndr_session_id):
        logger.info(
            f"Retrieving session for session ID ending in: f{self.redact_session_id}"
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
        except (KeyError, IndexError):
            raise AuthorisationException(
                f"Unable to find session for session ID ending in: {self.redact_session_id}"
            )

    def validate_login_session(self, session_expiry_time: float):
        time_now = time.time()
        if session_expiry_time <= time_now:
            raise AuthorisationException(
                f"The session is already expired for session ID ending in: {self.redact_session_id}"
            )
