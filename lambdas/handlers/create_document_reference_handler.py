import json
import os
import sys
from json import JSONDecodeError

from enums.logging_app_interaction import LoggingAppInteraction
from services.create_document_reference_service import CreateDocumentReferenceService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.lambda_exceptions import CreateDocumentRefException
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

sys.path.append(os.path.join(os.path.dirname(__file__)))

logger = LoggingService(__name__)


@set_request_context_for_logging
@ensure_environment_variables(
    names=[
        "LLOYD_GEORGE_BUCKET_NAME",
        "LLOYD_GEORGE_DYNAMODB_NAME",
        "DOCUMENT_STORE_BUCKET_NAME",
        "DOCUMENT_STORE_DYNAMODB_NAME",
    ]
)
@override_error_check
@handle_lambda_exceptions
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.UPLOAD_RECORD.value

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
            raise CreateDocumentRefException(400, "Missing event body")

        doc_list = body["content"][0]["attachment"]
        return nhs_number, doc_list

    except (JSONDecodeError, AttributeError) as e:
        logger.error(
            f"Invalid json in body: {str(e)}",
            {"Result": "Create document reference failed"},
        )
        raise CreateDocumentRefException(400, "Invalid json in body")
    except (KeyError, TypeError) as e:
        logger.error(
            f"Request body missing some properties: {str(e)}",
            {"Result": "Create document reference failed"},
        )
        raise CreateDocumentRefException(400, "Request body missing some properties")
