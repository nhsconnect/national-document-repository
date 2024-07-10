import json

from enums.logging_app_interaction import LoggingAppInteraction
from services.document_manifest_job_service import DocumentManifestJobService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.decorators.validate_document_type import validate_document_type
from utils.decorators.validate_manifest_job_id import validate_manifest_job_id
from utils.decorators.validate_patient_id import validate_patient_id
from utils.document_type_utils import extract_document_type_to_enum
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = LoggingService(__name__)


@validate_patient_id
@validate_document_type
def create_manifest_job(event, context):
    logger.info("Starting document manifest process")
    nhs_number = event["queryStringParameters"]["patientId"]
    document_type = extract_document_type_to_enum(
        event["queryStringParameters"]["docType"]
    )
    document_references = event["multiValueQueryStringParameters"].get("docReferences")

    request_context.patient_nhs_no = nhs_number

    document_manifest_service = DocumentManifestJobService()
    response = document_manifest_service.create_document_manifest_job(
        nhs_number, document_type, document_references
    )

    return ApiGatewayResponse(
        200, json.dumps({"jobId": response}), "POST"
    ).create_api_gateway_response()


@validate_manifest_job_id
def get_manifest_job(event, context):
    logger.info("Retrieving document manifest")

    job_id = event["queryStringParameters"]["jobId"]

    document_manifest_service = DocumentManifestJobService()
    response = document_manifest_service.query_document_manifest_job(job_id)

    return ApiGatewayResponse(
        200, json.dumps(response.model_dump(by_alias=True)), "GET"
    ).create_api_gateway_response()


@set_request_context_for_logging
@ensure_environment_variables(
    names=[
        "DOCUMENT_STORE_DYNAMODB_NAME",
        "LLOYD_GEORGE_DYNAMODB_NAME",
        "ZIPPED_STORE_BUCKET_NAME",
        "ZIPPED_STORE_DYNAMODB_NAME",
        "PRESIGNED_ASSUME_ROLE",
    ]
)
@override_error_check
@handle_lambda_exceptions
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.DOWNLOAD_RECORD.value

    method_handler = {"GET": get_manifest_job, "POST": create_manifest_job}
    http_method = event["httpMethod"]
    handler = method_handler[http_method]

    response = handler(event, context)
    return response
