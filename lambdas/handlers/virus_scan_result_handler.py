from enums.logging_app_interaction import LoggingAppInteraction
from services.virus_scan_result_service import VirusScanResultService
from utils.audit_logging_setup import LoggingService
from utils.decorators import handle_lambda_exceptions, override_error_check
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.request_context import request_context

logger = LoggingService(__name__)


@set_request_context_for_logging
@ensure_environment_variables(
    names=[
        "APPCONFIG_APPLICATION",
        "APPCONFIG_CONFIGURATION",
        "APPCONFIG_ENVIRONMENT",
        "STAGING_STORE_BUCKET_NAME",
    ]
)
@override_error_check
@handle_lambda_exceptions
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.VIRUS_SCAN.value
    virus_scan_result_service = VirusScanResultService()
    new_access_token = virus_scan_result_service.fetch_new_access_token()
    logger.info(f"access_token: {new_access_token}")


# scan_url = baseURL + '/api/Scan'
# form = encoder.MultipartEncoder({
#     "documents": ("my_file", file, "application/octet-stream"),
#     "composite": "NONE",
# })
# headers = {"Prefer": "respond-async", "Content-Type": form.content_type, 'Authorization': 'Bearer ' + access_token}
# r = session.post(scan_url, headers=headers, data=form, timeout=4000)

# parsed = json.loads(r.text)
