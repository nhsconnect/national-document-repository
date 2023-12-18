import os

from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from oauthlib.oauth2 import WebApplicationClient
from services.dynamo_service import DynamoDBService
from services.oidc_service import OidcService
from services.ssm_service import SSMService
from utils.audit_logging_setup import LoggingService
from utils.exceptions import AuthorisationException, LogoutFailureException

logger = LoggingService(__name__)


class BackChannelLogoutService:
    oidc_service = OidcService()
    dynamodb_service = DynamoDBService()

    def __init__(self):
        self.dynamodb_name = os.getenv("AUTH_DYNAMODB_NAME")

    def logout_handler(self, token):
        try:
            self.__class__.oidc_service.set_up_oidc_parameters(
                SSMService, WebApplicationClient
            )
            decoded_token = self.__class__.oidc_service.validate_and_decode_token(token)
            sid = decoded_token.get("sid", None)
            if not sid:
                raise LogoutFailureException("No sid field in decoded token")
            session_id = self.finding_session_id_by_sid(sid)
            if not session_id:
                raise LogoutFailureException("No session id was found for given sid")
            self.remove_session_from_dynamo_db(session_id)

        except AuthorisationException as e:
            logger.error(f"error while decoding JWT: {e}")
            raise LogoutFailureException("JWT was invalid")
        except ClientError as e:
            logger.error(f"Error logging out user: {e}")
            raise LogoutFailureException("Internal error logging user out")

    def finding_session_id_by_sid(self, sid):
        filter_sid = Attr("sid").eq(sid)
        db_response = self.__class__.dynamodb_service.scan_table(
            table_name=self.dynamodb_name, filter_expression=filter_sid
        )
        items = db_response.get("Items", None)
        if items and isinstance(items, list):
            ndr_session_id = items[0].get("NDRSessionId", None)
            return ndr_session_id
        return None

    def remove_session_from_dynamo_db(self, ndr_session_id):
        self.__class__.dynamodb_service.delete_item(
            key={"NDRSessionId": ndr_session_id}, table_name=self.dynamodb_name
        )

        logger.info(
            f"Session removed for NDRSessionId {ndr_session_id}",
            {"Result": "Successful logout"},
        )
