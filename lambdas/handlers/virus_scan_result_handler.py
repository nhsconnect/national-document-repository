import json
import os
from json import JSONDecodeError

from botocore.exceptions import ClientError
from enums.feature_flags import FeatureFlags
from enums.lambda_error import LambdaError
from enums.logging_app_interaction import LoggingAppInteraction
from enums.supported_document_types import SupportedDocumentTypes
from enums.virus_scan_result import VirusScanResult
from services.base.dynamo_service import DynamoDBService
from services.feature_flags_service import FeatureFlagService
from services.virus_scan_result_service import VirusScanService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.decorators.validate_patient_id import validate_patient_id
from utils.lambda_exceptions import FeatureFlagsException, VirusScanResultException
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = LoggingService(__name__)


@validate_patient_id
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
        nhs_number_query_string = event["queryStringParameters"]["patientId"]

        document_reference = event_body.get("documentReference")
        _, doc_type, nhs_number, _ = document_reference.split("/")
        if doc_type.upper() not in SupportedDocumentTypes.list():
            raise VirusScanResultException(400, LambdaError.VirusScanNoDocumentType)
        if nhs_number != nhs_number_query_string:
            raise VirusScanResultException(400, LambdaError.PatientIdMismatch)

    except (JSONDecodeError, KeyError):
        raise VirusScanResultException(400, LambdaError.VirusScanNoBody)
    except ValueError:
        raise VirusScanResultException(400, LambdaError.VirusScanNoDocumentType)

    lg_table_name = os.getenv("LLOYD_GEORGE_DYNAMODB_NAME")
    virus_scan_service = VirusScanService()
    scan_result = virus_scan_service.scan_file(document_reference)

    dynamo_service = DynamoDBService()
    file_id = document_reference.split("/")[-1]
    logger.info("Updating dynamo db table")
    updated_fields = {"VirusScannerResult": scan_result}
    if scan_result == VirusScanResult.INFECTED:
        updated_fields["DocStatus"] = "cancelled"
    try:
        dynamo_service.update_item(
            table_name=lg_table_name,
            key_pair={"ID": file_id},
            updated_fields=updated_fields,
        )
    except ClientError:
        raise VirusScanResultException(500, LambdaError.VirusScanAWSFailure)

    if scan_result == VirusScanResult.CLEAN:
        return ApiGatewayResponse(
            200, "Virus Scan was successful", "POST"
        ).create_api_gateway_response()
    else:
        raise VirusScanResultException(400, LambdaError.VirusScanUnclean)
