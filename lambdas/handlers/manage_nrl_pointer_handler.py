import json

from enums.nrl_sqs_upload import NrlActionTypes
from models.fhir.R4.nrl_fhir_document_reference import FhirDocumentReference
from models.nrl_sqs_message import NrlSqsMessage
from services.base.nhs_oauth_service import NhsOauthService
from services.base.ssm_service import SSMService
from services.nrl_api_service import NrlApiService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.request_context import request_context

logger = LoggingService(__name__)


@set_request_context_for_logging
@ensure_environment_variables(
    names=[
        "APPCONFIG_APPLICATION",
        "APPCONFIG_CONFIGURATION",
        "APPCONFIG_ENVIRONMENT",
        "NRL_API_ENDPOINT",
        "NRL_END_USER_ODS_CODE",
    ]
)
@handle_lambda_exceptions
def lambda_handler(event, context):
    logger.info(f"Received event: {event}")
    sqs_messages = event.get("Records", [])
    ssm_service = SSMService()
    oauth_service = NhsOauthService(ssm_service)
    nrl_api_service = NrlApiService(ssm_service, oauth_service)

    unhandled_messages = []

    for sqs_message in sqs_messages:
        try:
            sqs_message = json.loads(sqs_message["body"])
            nrl_message = NrlSqsMessage(**sqs_message)
            NrlSqsMessage.model_validate(nrl_message)
            request_context.patient_nhs_no = nrl_message.nhs_number
            logger.info(
                f"Processing SQS message for nhs number: {nrl_message.nhs_number}"
            )
            nrl_verified_message = nrl_message.model_dump(
                by_alias=True, exclude_none=True
            )
            match nrl_message.action:
                case NrlActionTypes.CREATE:
                    document = FhirDocumentReference(
                        **nrl_verified_message,
                        custodian=nrl_api_service.end_user_ods_code,
                    ).build_fhir_dict()

                    nrl_api_service.create_new_pointer(json.dumps(document))
                case NrlActionTypes.DELETE:
                    nrl_api_service.delete_pointer(
                        nrl_message.nhs_number, nrl_message.snomed_code_doc_type
                    )
        except Exception as error:
            unhandled_messages.append(sqs_message)
            logger.info(f"Failed to process current message due to error: {error}")
            logger.info("Continue on next message")
