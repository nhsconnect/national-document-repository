import os

from botocore.exceptions import ClientError
from enums.logging_app_interaction import LoggingAppInteraction
from enums.s3_lifecycle_tags import S3LifecycleTags
from enums.supported_document_types import SupportedDocumentTypes
from services.document_service import DocumentService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.decorators.validate_document_type import (extract_document_type,
                                                     validate_document_type)
from utils.decorators.validate_patient_id import validate_patient_id
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context
from utils.decorators.override_error_check import override_error_check

logger = LoggingService(__name__)


@set_request_context_for_logging
@validate_patient_id
@validate_document_type
@ensure_environment_variables(
    names=[
        "DOCUMENT_STORE_DYNAMODB_NAME",
        "LLOYD_GEORGE_DYNAMODB_NAME",
    ]
)
@override_error_check
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.DELETE_RECORD.value
    nhs_number = event["queryStringParameters"]["patientId"]
    doc_type = extract_document_type(event["queryStringParameters"]["docType"])
    request_context.patient_nhs_no = nhs_number
    document_service = DocumentService()

    try:
        if doc_type == SupportedDocumentTypes.ALL.value:
            arf_delete_response = handle_delete(
                document_service, nhs_number, str(SupportedDocumentTypes.ARF.value)
            )
            lg_delete_response = handle_delete(
                document_service, nhs_number, str(SupportedDocumentTypes.LG.value)
            )

            if (
                arf_delete_response["statusCode"] == 404
                and lg_delete_response["statusCode"] == 404
            ):
                return ApiGatewayResponse(
                    404, "No documents available", "DELETE"
                ).create_api_gateway_response()

            return ApiGatewayResponse(
                200, "Success", "DELETE"
            ).create_api_gateway_response()

        if doc_type == SupportedDocumentTypes.ARF.value:
            return handle_delete(
                document_service, nhs_number, str(SupportedDocumentTypes.ARF.value)
            )

        if doc_type == SupportedDocumentTypes.LG.value:
            return handle_delete(
                document_service, nhs_number, str(SupportedDocumentTypes.LG.value)
            )

    except ClientError as e:
        logger.info(str(e), {"Result": f"Unsuccessful deletion due to {str(e)}"})
        return ApiGatewayResponse(
            500, "Failed to delete documents", "DELETE"
        ).create_api_gateway_response()


def handle_delete(
    document_service: DocumentService, nhs_number: str, doc_type: str
) -> dict:
    table_name = ""
    if doc_type == SupportedDocumentTypes.ARF.value:
        table_name = os.environ["DOCUMENT_STORE_DYNAMODB_NAME"]
    if doc_type == SupportedDocumentTypes.LG.value:
        table_name = os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]

    results = document_service.fetch_available_document_references_by_type(
        nhs_number, doc_type
    )

    if not results:
        return ApiGatewayResponse(
            404, "No documents available", "DELETE"
        ).create_api_gateway_response()

    document_service.delete_documents(
        table_name=table_name,
        document_references=results,
        type_of_delete=str(S3LifecycleTags.SOFT_DELETE.value),
    )
    logger.info(
        "Documents were deleted successfully", {"Result": "Successful deletion"}
    )
    return ApiGatewayResponse(200, "Success", "DELETE").create_api_gateway_response()
