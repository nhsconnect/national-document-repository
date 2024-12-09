from services.dynamic_configuration_service import DynamicConfigurationService
from services.nrl_get_document_reference_service import NRLGetDocumentReferenceService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.lambda_response import ApiGatewayResponse

logger = LoggingService(__name__)


@handle_lambda_exceptions
@set_request_context_for_logging
@ensure_environment_variables(
    names=[
        "APPCONFIG_APPLICATION",
        "APPCONFIG_CONFIGURATION",
        "APPCONFIG_ENVIRONMENT",
        "LLOYD_GEORGE_DYNAMODB_NAME",
        "PRESIGNED_ASSUME_ROLE",
        "CLOUDFRONT_URL",
    ]
)
def lambda_handler(event, context):
    document_id = event["pathParameters"]["id"]
    bearer_token = event["headers"]["Authorization"]
    configuration_service = DynamicConfigurationService()
    configuration_service.set_auth_ssm_prefix()
    get_document_service = NRLGetDocumentReferenceService()
    placeholder = get_document_service.handle_get_document_reference_request(
        document_id, bearer_token
    )

    return ApiGatewayResponse(
        status_code=200, body=placeholder, methods="GET"
    ).create_api_gateway_response()
