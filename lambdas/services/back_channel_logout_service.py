import os

from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from oauthlib.oauth2 import WebApplicationClient
from services.base.dynamo_service import DynamoDBService
from services.base.ssm_service import SSMService
from services.oidc_service import OidcService
from utils.audit_logging_setup import LoggingService
from utils.exceptions import AuthorisationException, LogoutFailureException

logger = LoggingService(__name__)


class BackChannelLogoutService:
    def __init__(self):
        self.oidc_service = OidcService()
        self.dynamodb_service = DynamoDBService()
        self.dynamodb_name = os.getenv("AUTH_DYNAMODB_NAME")

    def logout_handler(self, token):
        try:
            self.oidc_service.set_up_oidc_parameters(SSMService, WebApplicationClient)
            decoded_token = self.oidc_service.validate_and_decode_token(token)
            sid = decoded_token.get("sid", None)
            if not sid:
                raise LogoutFailureException("No sid field in decoded token")
            session_id = self.finding_session_id_by_sid(sid)
            if not session_id:
                raise LogoutFailureException("No session id was found for given sid")
            self.remove_session_from_dynamo_db(session_id)

        except AuthorisationException as e:
            logger.error(f"Error while decoding JWT: {str(e)}")
            raise LogoutFailureException("JWT was invalid")
        except ClientError as e:
            logger.error(f"Error logging out user: {str(e)}")
            raise LogoutFailureException("Internal error logging user out")

    def finding_session_id_by_sid(self, sid):
        filter_sid = Attr("sid").eq(sid)
        db_response = self.dynamodb_service.scan_table(  # table is small so changing scan to query wouldn't give much value
            table_name=self.dynamodb_name, filter_expression=filter_sid
        )
        items = db_response.get("Items", None)
        if items and isinstance(items, list):
            ndr_session_id = items[0].get("NDRSessionId", None)
            return ndr_session_id
        return None

    def remove_session_from_dynamo_db(self, ndr_session_id):
        self.dynamodb_service.delete_item(
            key={"NDRSessionId": ndr_session_id}, table_name=self.dynamodb_name
        )

        logger.info(
            f"Session removed for NDRSessionId {ndr_session_id}",
            {"Result": "Successful logout"},
        )
