from enums.logging_app_interaction import LoggingAppInteraction
from services.search_patient_details_service import SearchPatientDetailsService
from utils.audit_logging_setup import LoggingService
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.decorators.validate_patient_id import validate_patient_id
from utils.exceptions import SearchPatientException
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = LoggingService(__name__)


@set_request_context_for_logging
@validate_patient_id
@override_error_check
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.PATIENT_SEARCH.value

    try:
        nhs_number = event["queryStringParameters"]["patientId"]
        request_context.patient_nhs_no = nhs_number
        user_ods_code, user_role = "", ""
        if isinstance(request_context.authorization, dict):
            user_ods_code = request_context.authorization.get(
                "selected_organisation", {}
            ).get("org_ods_code", "")
            user_role = request_context.authorization.get("repository_role", "")
        if not user_role or not user_ods_code:
            raise SearchPatientException(400, "Missing user details")
        print(f"user_role {user_role}")
        print(f"user_ods_code {user_ods_code}")

        search_service = SearchPatientDetailsService(user_role, user_ods_code)
        response = search_service.handle_search_patient_request(nhs_number)

        return ApiGatewayResponse(200, response, "GET").create_api_gateway_response()

    except SearchPatientException as e:
        logger.error(
            e.message, {"Result": f"Unsuccessful search due to {str(e.message)}"}
        )
        return ApiGatewayResponse(
            e.status_code, f"An error occurred due to: {str(e.message)}", "GET"
        ).create_api_gateway_response()
