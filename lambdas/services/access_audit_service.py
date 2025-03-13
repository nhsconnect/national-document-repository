import os

from enums.lambda_error import LambdaError
from models.access_audit import AccessAuditReason
from pydantic import ValidationError
from services.base.dynamo_service import DynamoDBService
from services.manage_user_session_access import ManageUserSessionAccess
from utils.audit_logging_setup import LoggingService
from utils.lambda_exceptions import AccessAuditException
from utils.request_context import request_context

logger = LoggingService(__name__)


class AccessAuditService:
    def __init__(self):
        self.audit_table = os.getenv("ACCESS_AUDIT_TABLE_NAME")
        self.manage_user_session_service = ManageUserSessionAccess()
        self.db_service = DynamoDBService()

    def manage_access_request(self, nhs_number, request: dict, request_type: str):
        audit_access_fields = self.arrange_access_request(
            nhs_number, request_type, request
        )
        self.write_to_access_audit_table(audit_access_fields)
        self.update_auth_session_table(nhs_number)

    def arrange_access_request(self, nhs_number, request_type, request: dict):
        ndr_session_id = request_context.authorization.get("ndr_session_id")
        user_id = request_context.authorization.get("nhs_user_id")
        user_ods_code = request_context.authorization.get(
            "selected_organisation", {}
        ).get("org_ods_code")
        try:
            audit_reason = AccessAuditReason(
                nhs_number=nhs_number,
                request_type=request_type,
                user_id=user_id,
                user_ods_code=user_ods_code,
                user_session_id=ndr_session_id,
                reason_codes=request.get("Reasons"),
                custom_reason=request.get("OtherReasonText"),
            )
        except ValidationError as e:
            logger.error(e)
            raise AccessAuditException(400, LambdaError.InvalidReasonInput)

        return audit_reason.model_dump(exclude_none=True, by_alias=True)

    def write_to_access_audit_table(self, audit_access_item):
        self.db_service.create_item(
            table_name=self.audit_table,
            item=audit_access_item,
        )

    def update_auth_session_table(self, nhs_number):
        self.manage_user_session_service.update_auth_session_with_permitted_search(
            nhs_number=nhs_number,
            write_to_deceased_column=False,
        )
