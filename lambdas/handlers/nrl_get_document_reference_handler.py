from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.exceptions import AuthorisationException
from utils.lambda_response import ApiGatewayResponse

logger = LoggingService(__name__)


@set_request_context_for_logging
@ensure_environment_variables(
    names=[
        "APPCONFIG_APPLICATION",
        "APPCONFIG_CONFIGURATION",
        "APPCONFIG_ENVIRONMENT",
        # "NRL_END_USER_ODS_CODE",
        "LLOYD_GEORGE_DYNAMODB_NAME",
        "LLOYD_GEORGE_BUCKET_NAME",
        "PRESIGNED_ASSUME_ROLE",
        "CLOUDFRONT_URL",
        "OIDC_USER_INFO_URL",
    ]
)
def lambda_handler(event, context):

    try:
        # # document_id = event["pathParameters"]["id"]
        # # bearer_token = event["headers"]["Authorization"]
        #
        # get_document_service = NRLGetDocumentReferenceService()

        #
        # def extract_document_details_from_event():
        #     pass

        placeholder = "cloudfront presigned url"

        return ApiGatewayResponse(status_code=200, body=placeholder, methods="GET")
    # except NoAvailableDocument() as error:
    #     return ApiGatewayResponse()

    except AuthorisationException() as error:
        return ApiGatewayResponse(status_code=403, body=error.body, methods="GET")
