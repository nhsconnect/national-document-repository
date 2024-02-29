import json

import requests
from enums.lambda_error import LambdaError
from enums.pds_ssm_parameters import SSMParameter
from services.base.ssm_service import SSMService
from utils.audit_logging_setup import LoggingService
from utils.decorators import handle_lambda_exceptions, override_error_check
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.lambda_exceptions import VirusScanResultException

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
    try:
        parameters = [
            SSMParameter.VIRUS_API_USER.value,
            SSMParameter.VIRUS_API_PASSWORD.value,
            SSMParameter.VIRUS_API_ACCESSTOKEN.value,
        ]

        baseURL = "https://ndr-dev-vcapi.cloudstoragesecapp.com"
        username, password = SSMService().get_ssm_parameters(
            parameters, with_decryption=True
        )

        logger.info(f"username: {username}")
        logger.info(f"password: {password}")

        json_login = json.dumps({"username": username, "password": password})
        token_url = baseURL + "/api/Token"

        session = requests.Session()
        r = session.post(
            token_url, data=json_login, headers={"Content-type": "application/json"}
        )

        json_response = json.loads(r.text)
        access_token = json_response["accessToken"]
        logger.info(f"access_token: {access_token}")
    except Exception as e:
        logger.error(
            f"{LambdaError.VirusScanNoToken.to_str()}: {str(e)}",
            {"Result": "Virus scan result failed"},
        )
        raise VirusScanResultException(500, LambdaError.VirusScanNoToken)


# scan_url = baseURL + '/api/Scan'
# form = encoder.MultipartEncoder({
#     "documents": ("my_file", file, "application/octet-stream"),
#     "composite": "NONE",
# })
# headers = {"Prefer": "respond-async", "Content-Type": form.content_type, 'Authorization': 'Bearer ' + access_token}
# r = session.post(scan_url, headers=headers, data=form, timeout=4000)

# parsed = json.loads(r.text)
