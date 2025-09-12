from enums.lloyd_george_pre_process_format import LloydGeorgePreProcessFormat
from services.bulk_upload.metadata_general_preprocessor import (
    MetadataGeneralPreprocessor,
)
from services.bulk_upload.metadata_usb_preprocessor import (
    MetadataUsbPreprocessorService,
)
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging

logger = LoggingService(__name__)


@set_request_context_for_logging
@override_error_check
@ensure_environment_variables(names=["STAGING_STORE_BUCKET_NAME"])
@handle_lambda_exceptions
def lambda_handler(event, _context):
    practice_directory = event.get("practiceDirectory")
    raw_pre_format_type = event.get("preFormatType")

    pre_processor_service = get_pre_process_service(raw_pre_format_type)
    if not practice_directory:
        logger.info(
            "Failed to start metadata pre-processor due to missing practice directory"
        )
        return

    logger.info(
        f"Starting metadata pre-processor for practice directory: {practice_directory}"
    )

    metadata_service = pre_processor_service(practice_directory)
    metadata_service.process_metadata()


def get_pre_process_service(raw_pre_format_type):
    try:
        pre_format_type = LloydGeorgePreProcessFormat(raw_pre_format_type)
        if pre_format_type == LloydGeorgePreProcessFormat.GENERAL:
            return MetadataGeneralPreprocessor
        elif pre_format_type == LloydGeorgePreProcessFormat.USB:
            return MetadataUsbPreprocessorService
    except ValueError:
        logger.warning(
            f"Invalid preFormatType: '{raw_pre_format_type}', defaulting to {LloydGeorgePreProcessFormat.GENERAL}."
        )
        return MetadataGeneralPreprocessor
