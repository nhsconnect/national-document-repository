import json
from json import JSONDecodeError

from enums.lambda_error import LambdaError
from enums.logging_app_interaction import LoggingAppInteraction
from models.sqs.pdf_stitching_sqs_message import PdfStitchingSqsMessage
from pydantic import ValidationError
from services.pdf_stitching_service import PdfStitchingService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.decorators.validate_sqs_message_event import validate_sqs_event
from utils.exceptions import OdsErrorException
from utils.lambda_exceptions import PdfStitchingException
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
def lambda_handler(event, context):
    pdf_stitching_service = PdfStitchingService()
    if any(
        record.get("eventSource") == "aws:sqs" for record in event.get("Records", [])
    ):
        return handle_sqs_request(event, pdf_stitching_service)
    else:
        return handle_manual_trigger(event, pdf_stitching_service)


def handle_sqs_request(event, pdf_stitching_service):
    request_context.app_interaction = LoggingAppInteraction.STITCH_RECORD.value

    logger.info("Received PDF Stitching SQS message event")
    event_message_records = event.get("Records")

    for message in event_message_records:
        try:
            request_context.patient_nhs_no = ""
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
            raise e
        except PdfStitchingException as e:
            if e.error is LambdaError.StitchRollbackError:
                return ApiGatewayResponse(
                    500, "Failed to process PDF stitching SQS message", "GET"
                ).create_api_gateway_response()
            raise e

    return ApiGatewayResponse(
        200, "Successfully processed PDF stitching SQS message", "GET"
    ).create_api_gateway_response()


def handle_manual_trigger(event, pdf_stitching_service):
    logger.info("Received PDF Stitching manual trigger event")
    ods_code = event.get("ods_code")
    if not ods_code:
        raise OdsErrorException("No ODS code provided")

    pdf_stitching_service.process_manual_trigger(ods_code=ods_code)

    return ApiGatewayResponse(
        200, "Successfully processed PDF stitching for a manual trigger", "GET"
    ).create_api_gateway_response()
