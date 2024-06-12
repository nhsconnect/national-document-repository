from services.data_collection_service import DataCollectionService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables_for_non_webapi
from utils.decorators.override_error_check import override_error_check

logger = LoggingService(__name__)


@ensure_environment_variables_for_non_webapi(
    names=[
        "LLOYD_GEORGE_DYNAMODB_NAME",
        "LLOYD_GEORGE_BUCKET_NAME",
        "DOCUMENT_STORE_DYNAMODB_NAME",
        "DOCUMENT_STORE_BUCKET_NAME",
        "WORKSPACE",
        "STATISTICS_TABLE",
    ]
)
@override_error_check
def lambda_handler(_event, _context):
    logger.info("Starting data collection process")
    service = DataCollectionService()
    service.collect_all_data_and_write_to_dynamodb()
