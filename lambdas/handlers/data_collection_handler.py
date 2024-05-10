from services.data_collection_service import DataCollectionService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check

logger = LoggingService(__name__)


@ensure_environment_variables(
    names=[
        "DOCUMENT_STORE_DYNAMODB_NAME",
        "DOCUMENT_STORE_BUCKET_NAME",
        "LLOYD_GEORGE_DYNAMODB_NAME",
        "LLOYD_GEORGE_BUCKET_NAME",
        "WORKSPACE",
        "STATISTICS_TABLE",
    ]
)
@override_error_check
@handle_lambda_exceptions
def lambda_handler(event, context):
    logger.info("Starting data collection process")
    service = DataCollectionService()
    service.collect_all_data_and_write_to_dynamodb()
