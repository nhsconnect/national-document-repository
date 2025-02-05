from enums.lambda_error import LambdaError
from services.dynamic_configuration_service import DynamicConfigurationService
from services.nrl_get_document_reference_service import NRLGetDocumentReferenceService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.lambda_exceptions import NRLGetDocumentReferenceException
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
    try:
        if not event:
            raise NRLGetDocumentReferenceException(
                400, LambdaError.DocumentReferenceInvalidRequest
            )

        bearer_token = event.get("headers", {}).get("Authorization", None)
        if not bearer_token:
            raise NRLGetDocumentReferenceException(
                401, LambdaError.DocumentReferenceUnauthorised
            )

        path_params = event.get("pathParameters", {}).get("id", None)
        document_id, snomed_code = get_id_and_snomed_from_path_parameters(path_params)

        if not document_id or not snomed_code:
            raise NRLGetDocumentReferenceException(
                404, LambdaError.DocumentReferenceNotFound
            )

        configuration_service = DynamicConfigurationService()
        configuration_service.set_auth_ssm_prefix()
        get_document_service = NRLGetDocumentReferenceService()
        document_ref = get_document_service.handle_get_document_reference_request(
            snomed_code, document_id, bearer_token
        )

        return ApiGatewayResponse(
            status_code=200, body=document_ref, methods="GET"
        ).create_api_gateway_response()
    except NRLGetDocumentReferenceException as e:
        return ApiGatewayResponse(
            status_code=e.status_code,
            body=e.error.create_error_response().create_error_fhir_response(
                e.error.value.get("fhir_coding")
            ),
            methods="GET",
        ).create_api_gateway_response()


def get_id_and_snomed_from_path_parameters(path_parameters):
    params = path_parameters.split("~")
    if len(params) == 2:
        return params[1], params[0]
    else:
        return None, None
