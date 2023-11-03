import logging
import os

from botocore.exceptions import ClientError
from enums.s3_lifecycle_tags import S3LifecycleTags
from enums.supported_document_types import SupportedDocumentTypes
from services.document_service import DocumentService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.validate_document_type import (extract_document_type,
                                                     validate_document_type)
from utils.decorators.validate_patient_id import validate_patient_id
from utils.lambda_response import ApiGatewayResponse
from utils.logging_formatter import LoggingFormatter
from services.sensitive_audit_service import SensitiveAuditService

from utils.decorators.set_request_id import set_request_id_for_logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = LoggingFormatter()
audit_handler = SensitiveAuditService()
log_handler = logging.StreamHandler()
log_handler.setFormatter(formatter)
audit_handler.setFormatter(formatter)

@set_request_id_for_logging
@validate_patient_id
@validate_document_type
@ensure_environment_variables(
    names=[
        "DOCUMENT_STORE_DYNAMODB_NAME",
        "LLOYD_GEORGE_DYNAMODB_NAME",
    ]
)
def lambda_handler(event, context):
    nhs_number = event["queryStringParameters"]["patientId"]
    doc_type = extract_document_type(event["queryStringParameters"]["docType"])

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
        logger.info(str(e))
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

    return ApiGatewayResponse(200, "Success", "DELETE").create_api_gateway_response()
