import os
import tempfile

from services.batch_update_ods_code import BatchUpdate
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging

logger = LoggingService(__name__)


@set_request_context_for_logging
@ensure_environment_variables(
    names=[
        "APPCONFIG_APPLICATION",
        "APPCONFIG_CONFIGURATION",
        "APPCONFIG_ENVIRONMENT",
        "LLOYD_GEORGE_DYNAMODB_NAME",
        "PDS_FHIR_IS_STUBBED",
    ]
)
@override_error_check
def lambda_handler(event, context):
    table_name = os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]
    tempdir = tempfile.mkdtemp()
    filename = "batch_update_progress.json"

    batch_update = BatchUpdate(
        table_name=table_name,
        progress_store_file_path=f"{tempdir}/{filename}",
    )

    batch_update.main()
