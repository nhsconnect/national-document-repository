import json
from typing import Any, Dict

from enums.lambda_error import LambdaError
from services.document_reference_search_service import DocumentReferenceSearchService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions_fhir
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.decorators.validate_patient_id import validate_patient_id_fhir
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = LoggingService(__name__)


@ensure_environment_variables(
    names=["DYNAMODB_TABLE_LIST", "DOCUMENT_RETRIEVE_ENDPOINT_APIM"]
)
@set_request_context_for_logging
@validate_patient_id_fhir
@handle_lambda_exceptions_fhir
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

    query_string = event.get("queryStringParameters", {})

    search_filters = {}
    nhs_number = None

    for key, value in query_string.items():
        if key == "type:identifier":
            search_file_type = value.split("|")[-1]
            search_filters["file_type"] = search_file_type
        elif key == "custodian:identifier":
            custodian = value.split("|")[-1]
            search_filters["custodian"] = custodian
        elif key == "subject:identifier":
            subject_identifier = query_string["subject:identifier"]
            nhs_number = subject_identifier.split("|")[-1]
            request_context.patient_nhs_no = nhs_number
        elif key == "next-page-token":
            pass
        else:
            logger.warning(f"Unknown query parameter: {key}")

    service = DocumentReferenceSearchService()
    document_references = service.get_document_references(
        nhs_number=nhs_number,
        return_fhir=True,
        additional_filters=search_filters,
    )

    if not document_references:
        logger.info(f"No document references found for NHS number: {nhs_number}")
        return ApiGatewayResponse(
            404,
            LambdaError.DocumentReferenceNotFound.create_error_response().create_error_fhir_response(
                LambdaError.DocumentReferenceNotFound.value.get("fhir_coding")
            ),
            "GET",
        ).create_api_gateway_response()

    return ApiGatewayResponse(
        200, json.dumps(document_references), "GET"
    ).create_api_gateway_response()
