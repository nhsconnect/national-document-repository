from boto3.dynamodb.types import TypeDeserializer
from enums.lambda_error import LambdaError
from enums.logging_app_interaction import LoggingAppInteraction
from models.stitch_trace import StitchTrace
from pydantic import ValidationError
from services.lloyd_george_generate_stitch_service import LloydGeorgeStitchService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.lambda_exceptions import GenerateManifestZipException
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = LoggingService(__name__)


@set_request_context_for_logging
@ensure_environment_variables(
    names=[
        "ZIPPED_STORE_BUCKET_NAME",
        "ZIPPED_STORE_DYNAMODB_NAME",
    ]
)
@override_error_check
@handle_lambda_exceptions
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.DOWNLOAD_RECORD.value

    logger.info("Triggered by Dynamo INSERT event")

    dynamo_records = event.get("Records")

    if not dynamo_records:
        logger.error("No records in event")
        return ApiGatewayResponse(400, "", "GET").create_api_gateway_response()

    for record in dynamo_records:
        new_stitch_trace = record.get("dynamodb", {}).get("NewImage")
        event_name = record.get("eventName")
        if (
            not new_stitch_trace
            or event_name != "INSERT"
            or not isinstance(new_stitch_trace, dict)
        ):
            logger.error("Incorrect event format")
            return ApiGatewayResponse(400, "", "GET").create_api_gateway_response()

        processed_stitch_trace = prepare_stitch_trace_data(new_stitch_trace)
        stitch_record_handler(processed_stitch_trace)

    return ApiGatewayResponse(200, "", "GET").create_api_gateway_response()


def stitch_record_handler(stitch_trace_item):
    try:
        stitch_trace = StitchTrace.model_validate(stitch_trace_item)

    except ValidationError as e:
        logger.error(
            f"{LambdaError.StitchDBValidation.to_str()}: {str(e)}",
            {"Result": "Failed to create document stitch"},
        )
        raise GenerateManifestZipException(
            status_code=500, error=LambdaError.StitchDBValidation
        )

    stitch_service = LloydGeorgeStitchService(stitch_trace)
    stitch_service.handle_stitch_request()


def prepare_stitch_trace_data(new_stitch_trace: dict) -> dict:
    deserialize = TypeDeserializer().deserialize
    parsed_dynamodb_items = {
        key: deserialize(dynamodb_value)
        for key, dynamodb_value in new_stitch_trace.items()
    }
    return parsed_dynamodb_items
