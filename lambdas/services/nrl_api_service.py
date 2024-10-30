import uuid

from services.base.nhs_oauth_service import NhsOauthService
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class NrlApiService(NhsOauthService):
    def __init__(self, ssm_service):
        super().__init__(ssm_service)
        self.headers = {
            "Authorization": f"Bearer {self.create_access_token()}",
            "Accept": "application/json",
        }

    def get_api_endpoint(self):
        pass

    def create_new_pointer(self, body, headers):
        self.set_x_request_id()

    def update_pointer(self):
        self.set_x_request_id()

    def delete_pointer(self):
        self.set_x_request_id()

    def set_x_request_id(self):
        self.headers["X-Request-ID"] = uuid.uuid4()
