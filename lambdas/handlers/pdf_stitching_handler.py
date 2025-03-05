import json
from json import JSONDecodeError

from enums.lambda_error import LambdaError
from enums.logging_app_interaction import LoggingAppInteraction
from models.sqs.pdf_stitching_sqs_message import PdfStitchingSqsMessage
from pydantic import ValidationError
from services.pdf_stitching_service import PdfStitchingService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.decorators.validate_sqs_message_event import validate_sqs_event
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = LoggingService(__name__)


@set_request_context_for_logging
@ensure_environment_variables(
    names=[
        "LLOYD_GEORGE_BUCKET_NAME",
        "LLOYD_GEORGE_DYNAMODB_NAME",
        "UNSTITCHED_LLOYD_GEORGE_DYNAMODB_NAME",
        "PDF_STITCHING_SQS_URL",
        "APIM_API_URL",
        "NRL_SQS_URL",
    ]
)
@override_error_check
@validate_sqs_event
@handle_lambda_exceptions
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.STITCH_RECORD.value

    logger.info("Received PDF Stitching SQS message event")
    event_message_records = event.get("Records")
    pdf_stitching_service = PdfStitchingService()

    for message in event_message_records:
        try:
            message_body = json.loads(message.get("body", ""))
            stitching_message = PdfStitchingSqsMessage.model_validate(message_body)
            request_context.patient_nhs_no = stitching_message.nhs_number
            pdf_stitching_service.process_message(stitching_message=stitching_message)
        except (JSONDecodeError, ValidationError) as e:
            logger.error("Malformed PDF Stitching SQS message")
            logger.error(
                f"Failed to parse PDF stitching from SQS message: {str(e)}",
                {"Results": "Failed to stitch PDF"},
            )
            return ApiGatewayResponse(
                status_code=400,
                body=LambdaError.SqsInvalidEvent.create_error_body(),
                methods="GET",
            ).create_api_gateway_response()

    return ApiGatewayResponse(
        200, "Successfully processed PDF stitching SQS message", "GET"
    ).create_api_gateway_response()
