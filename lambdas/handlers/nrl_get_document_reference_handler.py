from services.nrl_get_document_reference_service import NRLGetDocumentReferenceService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.lambda_response import ApiGatewayResponse

logger = LoggingService(__name__)


@set_request_context_for_logging
@ensure_environment_variables(
    names=[
        "APPCONFIG_APPLICATION",
        "APPCONFIG_CONFIGURATION",
        "APPCONFIG_ENVIRONMENT",
        "NRL_API_ENDPOINT",
        # "NRL_END_USER_ODS_CODE",
        "LLOYD_GEORGE_DYNAMODB_NAME",
        # "LLOYD_GEORGE_BUCKET_NAME",
        "PRESIGNED_ASSUME_ROLE",
        "CLOUDFRONT_URL",
        "OIDC_USER_INFO_URL",
    ]
)
def lambda_handler(event, context):

    get_document_service = NRLGetDocumentReferenceService()

    # document_id = event["pathParameters"]["id"]
    # bearer_token = event["headers"]["Authorization"]
    #
    # def extract_document_details_from_event():
    #     pass

    if not get_document_service.user_allowed_to_see_file():
        return ApiGatewayResponse(
            status_code=403, body="?"
        ).create_api_gateway_response()

    placeholder = "cloudfront presigned url"

    return ApiGatewayResponse(status_code=200, body=placeholder, methods="GET")
