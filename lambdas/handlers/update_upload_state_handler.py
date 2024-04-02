import json
from json import JSONDecodeError

from enums.lambda_error import LambdaError
from enums.logging_app_interaction import LoggingAppInteraction
from services.update_upload_state_service import UpdateUploadStateService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.lambda_exceptions import UpdateUploadStateException
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = LoggingService(__name__)


@set_request_context_for_logging
@override_error_check
@ensure_environment_variables(
    [
        "APPCONFIG_APPLICATION",
        "APPCONFIG_CONFIGURATION",
        "APPCONFIG_ENVIRONMENT",
        "DOCUMENT_STORE_DYNAMODB_NAME",
        "LLOYD_GEORGE_DYNAMODB_NAME",
    ]
)
@handle_lambda_exceptions
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.UPDATE_UPLOAD_STATE.value
    failed_message = "Update upload state failed"
    logger.info("Update upload state handler triggered")
    try:
        event_body = json.loads(event["body"])
        if not event_body or not isinstance(event_body, dict):
            logger.error(
                f"{LambdaError.UploadConfirmResultMissingBody.to_str()}",
                {"Result": failed_message},
            )
            raise UpdateUploadStateException(
                400, LambdaError.UpdateUploadStateMissingBody
            )
        logger.info("Using update upload service...")
        update_upload_state_service = UpdateUploadStateService()
        update_upload_state_service.handle_update_state(event_body)
        return ApiGatewayResponse(
            200, "Update upload state successful", "POST"
        ).create_api_gateway_response()

    except (JSONDecodeError, AttributeError) as e:
        logger.error(
            f"{LambdaError.UpdateUploadStateMissingBody.to_str()}: {str(e)}",
            {"Result": failed_message},
        )
        raise UpdateUploadStateException(400, LambdaError.UpdateUploadStateMissingBody)
    except (KeyError, TypeError) as e:
        logger.error(
            f"{LambdaError.UpdateUploadStateMissingBody.to_str()}: {str(e)}",
            {"Result": failed_message},
        )
        raise UpdateUploadStateException(400, LambdaError.UpdateUploadStateMissingBody)
