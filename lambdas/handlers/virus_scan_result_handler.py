import json
from json import JSONDecodeError

from enums.feature_flags import FeatureFlags
from enums.lambda_error import LambdaError
from enums.logging_app_interaction import LoggingAppInteraction
from enums.supported_document_types import SupportedDocumentTypes
from services.feature_flags_service import FeatureFlagService
from services.virus_scan_result_service import VirusScanService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.lambda_exceptions import FeatureFlagsException, VirusScanResultException
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = LoggingService(__name__)


@set_request_context_for_logging
@ensure_environment_variables(
    names=[
        "APPCONFIG_APPLICATION",
        "APPCONFIG_CONFIGURATION",
        "APPCONFIG_ENVIRONMENT",
        "DOCUMENT_STORE_DYNAMODB_NAME",
        "LLOYD_GEORGE_DYNAMODB_NAME",
        "STAGING_STORE_BUCKET_NAME",
    ]
)
@override_error_check
@handle_lambda_exceptions
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.VIRUS_SCAN.value
    feature_flag_service = FeatureFlagService()
    upload_flag_name = FeatureFlags.UPLOAD_LAMBDA_ENABLED.value
    upload_lambda_enabled_flag_object = feature_flag_service.get_feature_flags_by_flag(
        upload_flag_name
    )

    if not upload_lambda_enabled_flag_object[upload_flag_name]:
        logger.info("Feature flag not enabled, event will not be processed")
        raise FeatureFlagsException(500, LambdaError.FeatureFlagDisabled)
    try:
        event_body = json.loads(event["body"])
        if not event_body:
            raise VirusScanResultException(400, LambdaError.VirusScanNoBody)

        document_reference = event_body.get("documentReference")

        if not any(
            doctype in document_reference.upper()
            for doctype in [
                SupportedDocumentTypes.ARF.value,
                SupportedDocumentTypes.LG.value,
            ]
        ):
            raise VirusScanResultException(400, LambdaError.VirusScanNoDocumentType)

    except (JSONDecodeError, KeyError):
        raise VirusScanResultException(400, LambdaError.VirusScanNoBody)

    virus_scan_service = VirusScanService()
    virus_scan_service.scan_file(document_reference)

    return ApiGatewayResponse(
        200, "Virus Scan was successful", "POST"
    ).create_api_gateway_response()
