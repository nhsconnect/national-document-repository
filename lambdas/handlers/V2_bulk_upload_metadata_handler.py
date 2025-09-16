from services.V2_bulk_upload_metadata_service import V2BulkUploadMetadataService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging

logger = LoggingService(__name__)


@set_request_context_for_logging
@override_error_check
@ensure_environment_variables(
    names=["STAGING_STORE_BUCKET_NAME", "METADATA_SQS_QUEUE_URL"]
)
@handle_lambda_exceptions
def lambda_handler(event, _context):
    practice_directory = event.get("practiceDirectory", "")

    logger.info(
        f"Starting metadata processing for practice directory: {practice_directory}"
    )

    metadata_service = V2BulkUploadMetadataService(practice_directory)
    metadata_service.process_metadata()
