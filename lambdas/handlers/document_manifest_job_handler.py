import json

from enums.logging_app_interaction import LoggingAppInteraction
from services.document_manifest_service import DocumentManifestService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.decorators.validate_document_type import validate_document_type
from utils.decorators.validate_patient_id import validate_patient_id
from utils.document_type_utils import extract_document_type_to_enum
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = LoggingService(__name__)


def handle_post(event, context, document_manifest_service: DocumentManifestService):
    logger.info("Starting document manifest process")

    document_type = extract_document_type_to_enum(
        event["queryStringParameters"]["docType"]
    )
    document_references = event["multiValueQueryStringParameters"].get("docReferences")

    response = document_manifest_service.create_document_manifest_job(
        document_type, document_references
    )

    return ApiGatewayResponse(
        200, json.dumps({"jobId": response}), "POST"
    ).create_api_gateway_response()


# @validate_job_id
def handle_get(event, context, document_manifest_service: DocumentManifestService):
    logger.info("Retrieving document manifest")

    job_id = event["queryStringParameters"]["jobId"]
    response = document_manifest_service.create_document_manifest_presigned_url(job_id)

    logger.audit_splunk_info(
        "User has downloaded Lloyd George records",
        {"Result": "Successful download"},
    )

    return ApiGatewayResponse(200, response, "GET").create_api_gateway_response()


@set_request_context_for_logging
@validate_patient_id
@validate_document_type
@ensure_environment_variables(
    names=[
        "DOCUMENT_STORE_DYNAMODB_NAME",
        "LLOYD_GEORGE_DYNAMODB_NAME",
        "ZIPPED_STORE_DYNAMODB_NAME",
        "PRESIGNED_ASSUME_ROLE",
    ]
)
@override_error_check
@handle_lambda_exceptions
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.DOWNLOAD_RECORD.value
    nhs_number = event["queryStringParameters"]["patientId"]

    request_context.patient_nhs_no = nhs_number
    document_manifest_service = DocumentManifestService(nhs_number)

    method_handler = {"GET": handle_get, "POST": handle_post}
    http_method = event["httpMethod"]
    handler = method_handler[http_method]

    response = handler(event, context, document_manifest_service)
    return response