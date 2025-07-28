from aws_embedded_metrics import metric_scope
from models.staging_metadata import METADATA_FILENAME
from services.bulk_upload_metadata_service import BulkUploadMetadataService
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
@metric_scope
def lambda_handler(_event, _context, metrics):
    logger.info("Starting metadata reading process")

    metadata_service = BulkUploadMetadataService(metrics)
    metadata_service.process_metadata(METADATA_FILENAME)
