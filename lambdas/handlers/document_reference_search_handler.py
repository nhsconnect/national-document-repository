import json

from enums.logging_app_interaction import LoggingAppInteraction
from services.document_reference_search_service import DocumentReferenceSearchService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.decorators.validate_patient_id import (
    extract_nhs_number_from_event,
    validate_patient_id,
)
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = LoggingService(__name__)


@set_request_context_for_logging
@validate_patient_id
@ensure_environment_variables(names=["DYNAMODB_TABLE_LIST"])
@override_error_check
@handle_lambda_exceptions
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.VIEW_PATIENT.value
    logger.info("Starting document reference search process")

    nhs_number = extract_nhs_number_from_event(event)
    request_context.patient_nhs_no = nhs_number

    document_reference_search_service = DocumentReferenceSearchService()
    response = document_reference_search_service.get_document_references(nhs_number)
    logger.info("User is able to view docs", {"Result": "Successful viewing docs"})

    if response:
        return ApiGatewayResponse(
            200, json.dumps(response), "GET"
        ).create_api_gateway_response()
    else:
        return ApiGatewayResponse(
            204, json.dumps([]), "GET"
        ).create_api_gateway_response()
