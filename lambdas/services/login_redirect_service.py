import os
import time

from botocore.exceptions import ClientError
from oauthlib.oauth2 import InsecureTransportError, WebApplicationClient
from services.dynamo_service import DynamoDBService
from services.ssm_service import SSMService
from utils.audit_logging_setup import LoggingService
from utils.exceptions import LoginRedirectException

logger = LoggingService(__name__)


class LoginRedirectService:
    def __init__(self):
        self.ssm_service = SSMService()
        self.dynamodb_service = DynamoDBService()
        self.oidc_parameters = {}

    def configure_oidc(self) -> WebApplicationClient:
        self.oidc_parameters = self.ssm_service.get_ssm_parameters(
            ["OIDC_AUTHORISE_URL", "OIDC_CLIENT_ID"]
        )

        return WebApplicationClient(
            client_id=self.oidc_parameters["OIDC_CLIENT_ID"],
        )

    def prepare_redirect_response(self):
        try:
            oidc_client = self.configure_oidc()

            url, _headers, _body = oidc_client.prepare_authorization_request(
                authorization_url=self.oidc_parameters["OIDC_AUTHORISE_URL"],
                redirect_url=os.environ["OIDC_CALLBACK_URL"],
                scope=[
                    "openid",
                    "profile",
                    "nhsperson",
                    "nationalrbacaccess",
                    "selectedrole",
                ],
                prompt="login",
            )

            self.save_state_in_dynamo_db(oidc_client.state)
            location_header = {"Location": url}
            logger.info(
                "User was successfully redirected to CIS2",
                {"Result": "Successful redirect"},
            )

        except (ClientError, InsecureTransportError) as e:
            logger.error(str(e), {"Result": "Unsuccessful redirect"})
            raise LoginRedirectException(500, "Server error")

        return location_header

    def save_state_in_dynamo_db(self, state):
        dynamodb_name = os.environ["AUTH_DYNAMODB_NAME"]
        ten_minutes = 60 * 10
        ttl = round(time.time()) + ten_minutes
        item = {"State": state, "TimeToExist": ttl}
        self.dynamodb_service.create_item(item=item, table_name=dynamodb_name)
