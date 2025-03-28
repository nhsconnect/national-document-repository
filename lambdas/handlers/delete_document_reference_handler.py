from enums.lambda_error import LambdaError
from enums.logging_app_interaction import LoggingAppInteraction
from services.document_deletion_service import DocumentDeletionService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.decorators.validate_document_type import validate_document_type
from utils.decorators.validate_patient_id import (
    extract_nhs_number_from_event,
    validate_patient_id,
)
from utils.document_type_utils import extract_document_type_to_enum
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = LoggingService(__name__)


@set_request_context_for_logging
@validate_patient_id
@validate_document_type
@ensure_environment_variables(
    names=[
        "DOCUMENT_STORE_DYNAMODB_NAME",
        "LLOYD_GEORGE_DYNAMODB_NAME",
        "UNSTITCHED_LLOYD_GEORGE_DYNAMODB_NAME",
    ]
)
@override_error_check
@handle_lambda_exceptions
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.DELETE_RECORD.value

    logger.info("Delete Document Reference handler has been triggered")

    nhs_number = extract_nhs_number_from_event(event)
    document_types = extract_document_type_to_enum(
        event["queryStringParameters"]["docType"]
    )

    request_context.patient_nhs_no = nhs_number

    deletion_service = DocumentDeletionService()

    files_deleted = deletion_service.handle_reference_delete(nhs_number, document_types)
    if files_deleted:
        logger.info(
            "Documents were deleted successfully", {"Result": "Successful deletion"}
        )
        return ApiGatewayResponse(
            200, "Success", "DELETE"
        ).create_api_gateway_response()
    else:
        logger.error(
            LambdaError.DocDelNull.to_str(),
            {"Result": "No documents available"},
        )

        return ApiGatewayResponse(
            404,
            LambdaError.DocDelNull.create_error_body(),
            "DELETE",
        ).create_api_gateway_response()
