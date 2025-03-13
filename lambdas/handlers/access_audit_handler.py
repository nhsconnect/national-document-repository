import json

from enums.lambda_error import LambdaError
from services.access_audit_service import AccessAuditService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.decorators.validate_patient_id import validate_patient_id
from utils.lambda_exceptions import AccessAuditException
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context


@set_request_context_for_logging
@validate_patient_id
@override_error_check
@ensure_environment_variables(
    names=["AUTH_SESSION_TABLE_NAME", "ACCESS_AUDIT_TABLE_NAME"]
)
@handle_lambda_exceptions
def lambda_handler(event, context):
    nhs_number = event.get("queryStringParameters").get("patientId")
    request_type = event.get("queryStringParameters", {}).get("accessAuditType")
    body = json.loads(event.get("body"))
    if not request_type or not body:
        raise AccessAuditException(400, LambdaError.InvalidReasonInput)
    request_context.patient_nhs_no = nhs_number
    access_audit_service = AccessAuditService()
    access_audit_service.manage_access_request(nhs_number, body, request_type)
    return ApiGatewayResponse(200, "", "POST").create_api_gateway_response()
