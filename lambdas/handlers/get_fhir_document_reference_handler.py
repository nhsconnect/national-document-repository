from enums.lambda_error import LambdaError
from oauthlib.oauth2 import WebApplicationClient
from services.base.ssm_service import SSMService
from services.dynamic_configuration_service import DynamicConfigurationService
from services.get_fhir_document_reference_service import GetFhirDocumentReferenceService
from services.oidc_service import OidcService
from services.search_patient_details_service import SearchPatientDetailsService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.exceptions import OidcApiException
from utils.lambda_exceptions import (
    GetFhirDocumentReferenceException,
    SearchPatientException,
)
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
            raise GetFhirDocumentReferenceException(
                400, LambdaError.DocumentReferenceInvalidRequest
            )
        bearer_token = event.get("headers", {}).get("Authorization", None)
        selected_role_id = event.get("headers", {}).get("cis2-urid", None)
        if not bearer_token:
            raise GetFhirDocumentReferenceException(
                401, LambdaError.DocumentReferenceUnauthorised
            )

        path_params = event.get("pathParameters", {}).get("id", None)
        document_id, snomed_code = get_id_and_snomed_from_path_parameters(path_params)

        if not document_id or not snomed_code:
            raise GetFhirDocumentReferenceException(
                404, LambdaError.DocumentReferenceNotFound
            )
        smartcard_role_code = None
        org_ods_code = None
        if selected_role_id:

            configuration_service = DynamicConfigurationService()
            configuration_service.set_auth_ssm_prefix()

            oidc_service = OidcService()
            oidc_service.set_up_oidc_parameters(SSMService, WebApplicationClient)
            userinfo = oidc_service.fetch_userinfo(bearer_token)
            org_ods_code = oidc_service.fetch_user_org_code(userinfo, selected_role_id)
            smartcard_role_code, user_id = oidc_service.fetch_user_role_code(
                userinfo, selected_role_id, "R"
            )
        get_document_service = GetFhirDocumentReferenceService()
        document_reference = get_document_service.handle_get_document_reference_request(
            snomed_code,
            document_id,
        )

        search_patient_service = SearchPatientDetailsService(
            smartcard_role_code, org_ods_code
        )
        try:
            search_patient_service.handle_search_patient_request(
                document_reference.nhs_number, True
            )

        except SearchPatientException:
            raise GetFhirDocumentReferenceException(
                403, LambdaError.DocumentReferenceForbidden
            )

        document_reference_response = (
            get_document_service.create_document_reference_fhir_response(
                document_reference
            )
        )

        return ApiGatewayResponse(
            status_code=200, body=document_reference_response, methods="GET"
        ).create_api_gateway_response()
    except (GetFhirDocumentReferenceException, OidcApiException) as e:
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
