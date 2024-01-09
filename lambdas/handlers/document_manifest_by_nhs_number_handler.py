from enums.logging_app_interaction import LoggingAppInteraction
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.decorators.validate_document_type import (
    validate_document_type,
)
from utils.decorators.validate_patient_id import validate_patient_id
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
        "ZIPPED_STORE_BUCKET_NAME",
        "ZIPPED_STORE_DYNAMODB_NAME",
    ]
)
@override_error_check
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.DOWNLOAD_RECORD.value
    logger.info("Starting document manifest process")
    # try:
    #     nhs_number = event["queryStringParameters"]["patientId"]
    #     doc_type = extract_document_type_as_enum(
    #         event["queryStringParameters"]["docType"]
    #     )
    #     request_context.patient_nhs_no = nhs_number
    #
    #     document_manifest_service = DocumentManifestService(nhs_number)
    #     response = document_manifest_service.create_document_manifest_presigned_url(
    #         doc_type
    #     )
    #
    #     logger.audit_splunk_info(
    #         "User has downloaded Lloyd George records",
    #         {"Result": "Successful download"},
    #     )
    #
    #     return ApiGatewayResponse(200, response, "GET").create_api_gateway_response()
    #
    # except DocumentManifestServiceException as e:
    #     logger.error(str(e), {"Result": f"Unsuccessful download due to {str(e)}"})
    #     return ApiGatewayResponse(
    #         e.status_code,
    #         f"An error occurred when creating document manifest: {str(e.message)}",
    #         "GET",
    #     ).create_api_gateway_response()
    # except ClientError as e:
    # logger.error(str(e), {"Result": f"Unsuccessful download due to {str(e)}"})
    response = ApiGatewayResponse(
        500, "An error occurred when creating document manifest", "GET"
    ).create_api_gateway_response()
    return response
