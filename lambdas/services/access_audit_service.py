import os

from services.base.dynamo_service import DynamoDBService
from services.manage_user_session_access import ManageUserSessionAccess
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class AccessAuditService:
    def __init__(self):
        self.audit_table = os.getenv("ACCESS_AUDIT_TABLE_NAME")
        self.manage_user_session_service = ManageUserSessionAccess()
        self.db_service = DynamoDBService()

    def write_to_access_audit_table(self, ndr_session_id, updated_fields):
        self.db_service.update_item(
            table_name=self.audit_table,
            key_pair={"NDRSessionId": ndr_session_id},
            updated_fields=updated_fields,
        )

    def update_auth_session_table(self, nhs_number):
        self.manage_user_session_service.update_auth_session_with_permitted_search(
            nhs_number=nhs_number,
            write_to_deceased_column=False,
        )
