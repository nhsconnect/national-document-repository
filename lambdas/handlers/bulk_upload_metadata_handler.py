import pydantic
from botocore.exceptions import ClientError
from models.staging_metadata import METADATA_FILENAME
from services.bulk_upload_metadata_service import BulkUploadMetadataService
from utils.audit_logging_setup import LoggingService
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging

logger = LoggingService(__name__)


@set_request_context_for_logging
@override_error_check
def lambda_handler(_event, _context):
    try:
        logger.info("Starting metadata reading process")

        metadata_service = BulkUploadMetadataService()
        metadata_service.process_metadata(METADATA_FILENAME)

    except pydantic.ValidationError as e:
        logger.info(
            "Failed to parse metadata.csv", {"Result": "Unsuccessful bulk upload"}
        )
        logger.error(str(e))
    except KeyError as e:
        logger.info("Failed due to missing key", {"Result": "Unsuccessful bulk upload"})
        logger.error(str(e))
    except ClientError as e:
        logger.error(str(e))
        if "HeadObject" in str(e):
            logger.error(
                f'No metadata file could be found with the name "{METADATA_FILENAME}"',
                {"Result": "Unsuccessful bulk upload"},
            )
