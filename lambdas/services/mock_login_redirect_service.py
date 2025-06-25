# import os
import random
import re
import string

from services.login_redirect_service import LoginRedirectService
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class MockLoginRedirectService(LoginRedirectService):

    def prepare_redirect_response(self, event):
        mock_login_route = self.ssm_service.get_ssm_parameter(
            self.ssm_prefix + "MOCK_LOGIN_ROUTE"
        )

        host = event["headers"].get("Host")
        clean_url = re.sub(r"^https?://api-", "https://", host)

        logger.info(f"Mock login clean url: {clean_url}")

        url = f"https://{clean_url}{mock_login_route}"

        state = "".join(random.choices(string.ascii_letters + string.digits, k=30))

        self.save_state_in_dynamo_db(state)
        location_header = {"Location": url}
        logger.info(
            "User was successfully redirected to MockLoginPage",
            {"Result": "Successful redirect"},
        )
        return location_header
