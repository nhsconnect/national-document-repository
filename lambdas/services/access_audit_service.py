import os

from enums.deceased_access_reason import DeceasedAccessReason
from enums.lambda_error import LambdaError
from models.access_audit import AccessAuditReason
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
        self.validate_reasons = []
        self.validate_other_reason_content = None

    def manage_access_request(self, nhs_number, request):
        self.validate_request(request)

    def validate_request(self, request):
        reasons = request.get("Reasons", [])
        validate_reasons = []
        for reason in reasons:
            if reason not in DeceasedAccessReason.list():
                raise AccessAuditException(400, LambdaError.InvalidReasonInput)
            validate_reasons.append(DeceasedAccessReason(reason))
        if not validate_reasons:
            raise AccessAuditException(400, LambdaError.InvalidReasonInput)
        other_reason_content = request.get("OtherReasonText", "")
        if DeceasedAccessReason.REASON06 in validate_reasons and other_reason_content:
            if len(other_reason_content) > 10000:
                raise AccessAuditException(400, LambdaError.InvalidReasonInput)
            self.validate_other_reason_content = other_reason_content

    def arrange_access_request(self, nhs_number):
        ndr_session_id = request_context.authorization.get("ndr_session_id")
        user_id = request_context.authorization.get("nhs_user_id")
        user_ods_code = request_context.authorization.get(
            "selected_organisation", {}
        ).get("org_ods_code")
        audit_reason = AccessAuditReason(
            type=f"LloydGeorge#{nhs_number}#DECE",
            user_id=user_id,
            user_ods_code=user_ods_code,
            user_session_id=ndr_session_id,
            reason_codes=self.validate_reasons,
            custom_reason=self.validate_other_reason_content,
        )
        print(audit_reason.model_dump(exclude_none=True, by_alias=True))

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
