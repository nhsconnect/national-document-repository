import json
from typing import Any, Dict

from services.document_reference_search_service import DocumentReferenceSearchService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.decorators.validate_patient_id import (
    extract_nhs_number_from_event,
    validate_patient_id,
)
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = LoggingService(__name__)


@ensure_environment_variables(names=["DYNAMODB_TABLE_LIST"])
@set_request_context_for_logging
@handle_lambda_exceptions
@validate_patient_id
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for searching document references by NHS number.

    Args:
        event: API Gateway event containing query parameters with NHS number
        context: Lambda context

    Returns:
        API Gateway response containing FHIR document references or 204 if none is found
    """
    logger.info("Received request to search for document references")

    nhs_number = extract_nhs_number_from_event(event)
    request_context.patient_nhs_no = nhs_number

    service = DocumentReferenceSearchService()
    document_references = service.get_document_references(
        nhs_number=nhs_number, return_fhir=True
    )

    if not document_references:
        logger.info(f"No document references found for NHS number: {nhs_number}")
        return ApiGatewayResponse(
            204, json.dumps([]), "GET"
        ).create_api_gateway_response()

    logger.info(f"Found {len(document_references)} document references")
    return ApiGatewayResponse(
        200, json.dumps(document_references), "GET"
    ).create_api_gateway_response()
