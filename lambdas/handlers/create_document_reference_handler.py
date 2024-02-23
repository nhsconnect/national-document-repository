import json
import os
import sys
from json import JSONDecodeError

from enums.feature_flags import FeatureFlags
from enums.lambda_error import LambdaError
from enums.logging_app_interaction import LoggingAppInteraction
from services.create_document_reference_service import CreateDocumentReferenceService
from services.feature_flags_service import FeatureFlagService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.lambda_exceptions import CreateDocumentRefException, FeatureFlagsException
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

sys.path.append(os.path.join(os.path.dirname(__file__)))

logger = LoggingService(__name__)


@set_request_context_for_logging
@ensure_environment_variables(
    names=[
        "APPCONFIG_APPLICATION",
        "APPCONFIG_CONFIGURATION",
        "APPCONFIG_ENVIRONMENT",
        "DOCUMENT_STORE_BUCKET_NAME",
        "DOCUMENT_STORE_DYNAMODB_NAME",
        "LLOYD_GEORGE_BUCKET_NAME",
        "LLOYD_GEORGE_DYNAMODB_NAME",
    ]
)
@override_error_check
@handle_lambda_exceptions
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.UPLOAD_RECORD.value

    feature_flag_service = FeatureFlagService()
    upload_flag_name = FeatureFlags.UPLOAD_LAMBDA_ENABLED.value
    upload_lambda_enabled_flag_object = feature_flag_service.get_feature_flags_by_flag(
        upload_flag_name
    )

    print(upload_lambda_enabled_flag_object)
    print(upload_lambda_enabled_flag_object[upload_flag_name])
    if not upload_lambda_enabled_flag_object[upload_flag_name]:
        logger.info("Feature flag not enabled, event will not be processed")
        raise FeatureFlagsException(500, LambdaError.FeatureFlagDisabled)

    logger.info("Starting document reference creation process")

    nhs_number, doc_list = processing_event_details(event)
    request_context.patient_nhs_no = nhs_number

    logger.info("Processed upload documents from request")
    docs_services = CreateDocumentReferenceService(nhs_number)
    docs_services.create_document_reference_request(doc_list)

    return ApiGatewayResponse(
        200, json.dumps(docs_services.url_responses), "POST"
    ).create_api_gateway_response()


def processing_event_details(event):
    try:
        body = json.loads(event["body"])
        nhs_number = body["subject"]["identifier"]["value"]

        if not body or not isinstance(body, dict):
            logger.error(
                f"{LambdaError.CreateDocNoBody.to_str()}",
                {"Result": "Create document reference failed"},
            )
            raise CreateDocumentRefException(400, LambdaError.CreateDocNoBody)

        doc_list = body["content"][0]["attachment"]
        return nhs_number, doc_list

    except (JSONDecodeError, AttributeError) as e:
        logger.error(
            f"{LambdaError.CreateDocPayload.to_str()}: {str(e)}",
            {"Result": "Create document reference failed"},
        )
        raise CreateDocumentRefException(400, LambdaError.CreateDocPayload)
    except (KeyError, TypeError) as e:
        logger.error(
            f"{LambdaError.CreateDocProps.to_str()}: {str(e)}",
            {"Result": "Create document reference failed"},
        )
        raise CreateDocumentRefException(400, LambdaError.CreateDocProps)
