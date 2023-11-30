import os
import time

from botocore.exceptions import ClientError
from oauthlib.oauth2 import InsecureTransportError
from services.dynamo_service import DynamoDBService
from utils.audit_logging_setup import LoggingService
from utils.lambda_response import ApiGatewayResponse

logger = LoggingService(__name__)


class LoginRedirectService:
    def prepare_redirect_response(self, web_application_client_class, ssm_service):
        try:
            oidc_parameters = ssm_service.get_ssm_parameters(
                ["OIDC_AUTHORISE_URL", "OIDC_CLIENT_ID"]
            )

            oidc_client = web_application_client_class(
                client_id=oidc_parameters["OIDC_CLIENT_ID"],
            )

            url, _headers, _body = oidc_client.prepare_authorization_request(
                authorization_url=oidc_parameters["OIDC_AUTHORISE_URL"],
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
            logger.error(f"Error: {e}", {"Result": "Unsuccessful redirect"})
            return ApiGatewayResponse(
                500, "Server error", "GET"
            ).create_api_gateway_response()
        return ApiGatewayResponse(303, "", "GET").create_api_gateway_response(
            headers=location_header
        )

    @staticmethod
    def save_state_in_dynamo_db(state):
        dynamodb_name = os.environ["AUTH_DYNAMODB_NAME"]
        dynamodb_service = DynamoDBService()
        ten_minutes = 60 * 10
        ttl = round(time.time()) + ten_minutes
        item = {"State": state, "TimeToExist": ttl}
        dynamodb_service.create_item(item=item, table_name=dynamodb_name)
