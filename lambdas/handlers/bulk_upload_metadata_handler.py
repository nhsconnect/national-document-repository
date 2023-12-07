from models.staging_metadata import METADATA_FILENAME
from services.bulk_upload_metadata_service import BulkUploadMetadataService
from utils.audit_logging_setup import LoggingService
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging

logger = LoggingService(__name__)


@set_request_context_for_logging
@override_error_check
def lambda_handler(_event, _context):
    logger.info("Starting metadata reading process")

    metadata_service = BulkUploadMetadataService()
    metadata_service.process_metadata(METADATA_FILENAME)
