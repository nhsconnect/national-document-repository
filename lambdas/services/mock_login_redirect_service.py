import os
import random
import re
import string

from enums.lambda_error import LambdaError
from services.login_redirect_service import LoginRedirectService
from utils.audit_logging_setup import LoggingService
from utils.constants.routes import MOCK_LOGIN_ROUTE
from utils.lambda_exceptions import LoginRedirectException

logger = LoggingService(__name__)


class MockLoginRedirectService(LoginRedirectService):

    def prepare_redirect_response(self, event):
        referer = event.get("headers", {}).get("Referer")
        if not referer:
            logger.error(
                "Referer header not found in request",
                {"Result": "Unsuccessful redirect"},
            )
            raise LoginRedirectException(500, LambdaError.RedirectClient)

        state = "".join(random.choices(string.ascii_letters + string.digits, k=30))
        self.save_state_in_dynamo_db(state)

        url = f"{referer}{MOCK_LOGIN_ROUTE}?state={state}"

        location_header = {"Location": url}
        logger.info(
            "User was successfully redirected to MockLoginPage",
            {"Result": "Successful redirect"},
        )
        return location_header
