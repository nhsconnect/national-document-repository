import json

from enums.logging_app_interaction import LoggingAppInteraction
from services.lloyd_george_stitch_job_service import LloydGeorgeStitchJobService
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


@validate_patient_id
def create_stitch_job(event, context):
    request_context.app_interaction = LoggingAppInteraction.VIEW_LG_RECORD.value
    logger.info("Lloyd George stitching handler triggered")
    nhs_number = extract_nhs_number_from_event(event)

    request_context.patient_nhs_no = nhs_number

    document_stitch_service = LloydGeorgeStitchJobService()
    job_status = document_stitch_service.get_or_create_stitch_job(nhs_number)

    return ApiGatewayResponse(
        200, json.dumps({"jobStatus": job_status}), "POST"
    ).create_api_gateway_response()


@validate_patient_id
def get_stitch_job(event, context):
    logger.info("Retrieving document stitch")

    nhs_number = extract_nhs_number_from_event(event)

    document_stitch_service = LloydGeorgeStitchJobService()
    response = document_stitch_service.query_document_stitch_job(nhs_number)

    return ApiGatewayResponse(
        200, json.dumps(response.model_dump(by_alias=True)), "GET"
    ).create_api_gateway_response()


@override_error_check
@set_request_context_for_logging
@handle_lambda_exceptions
@ensure_environment_variables(
    names=[
        "LLOYD_GEORGE_DYNAMODB_NAME",
        "LLOYD_GEORGE_BUCKET_NAME",
        "PRESIGNED_ASSUME_ROLE",
        "CLOUDFRONT_URL",
        "STITCH_METADATA_DYNAMODB_NAME",
    ]
)
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.DOWNLOAD_RECORD.value

    method_handler = {"GET": get_stitch_job, "POST": create_stitch_job}
    http_method = event["httpMethod"]
    handler = method_handler[http_method]

    response = handler(event, context)
    return response
