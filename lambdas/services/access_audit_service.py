import os

from services.authoriser_service import AuthoriserService
from services.base.dynamo_service import DynamoDBService
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class AccessAuditService:
    def __init__(self):
        self.dynamodb_service = DynamoDBService()
        self.auth_service = AuthoriserService()
        self.audit_table = self.dynamodb_service.get_table("access_audit")
        self.session_table_name = os.getenv("AUTH_SESSION_TABLE_NAME")

    def write_to_access_audit_table(self):
        pass

    def update_auth_audit_table(self):
        pass
