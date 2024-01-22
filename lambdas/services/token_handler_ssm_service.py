from enums.lambda_error import LambdaError
from services.base.ssm_service import SSMService
from utils.audit_logging_setup import LoggingService
from utils.constants.ssm import (
    GP_ADMIN_USER_ROLE_CODES,
    GP_CLINICAL_USER_ROLE_CODE,
    GP_ORG_ROLE_CODE,
    PCSE_ODS_CODE,
    PCSE_USER_ROLE_CODE,
)
from utils.lambda_exceptions import LoginException

logger = LoggingService(__name__)


class TokenHandlerSSMService(SSMService):
    def __init__(self):
        super().__init__()

    def get_smartcard_role_codes(self) -> list[str]:
        logger.info("starting ssm request to retrieve required smartcard role codes")
        params = self.get_ssm_parameters(
            [
                GP_ADMIN_USER_ROLE_CODES,
                GP_CLINICAL_USER_ROLE_CODE,
                PCSE_USER_ROLE_CODE,
            ]
        )

        response = [
            params.get(GP_ADMIN_USER_ROLE_CODES),
            params.get(GP_CLINICAL_USER_ROLE_CODE),
            params.get(PCSE_USER_ROLE_CODE),
        ]

        if None in response:
            logger.error(
                LambdaError.LoginBadSSM.to_str(),
                {"Result": "Unsuccessful login"},
            )
            raise LoginException(500, LambdaError.LoginNoSSM)

        return response

    def get_smartcard_role_gp_admin(self) -> list[str]:
        logger.info(
            "starting ssm request to retrieve required smartcard role code gp admin"
        )
        params = self.get_ssm_parameters([GP_ADMIN_USER_ROLE_CODES])
        values = params.get(GP_ADMIN_USER_ROLE_CODES)

        if values is None:
            logger.error(
                LambdaError.LoginAdminSSM.to_str(),
                {"Result": "Unsuccessful login"},
            )
            raise LoginException(500, LambdaError.LoginAdminSSM)

        response = values.split(",")
        return response

    def get_smartcard_role_gp_clinical(self) -> str:
        logger.info(
            "starting ssm request to retrieve required smartcard role code gp clinical"
        )
        params = self.get_ssm_parameters([GP_CLINICAL_USER_ROLE_CODE])

        response = params.get(GP_CLINICAL_USER_ROLE_CODE)
        if response is None:
            logger.error(
                LambdaError.LoginClinicalSSM.to_str(),
                {"Result": "Unsuccessful login"},
            )
            raise LoginException(500, LambdaError.LoginClinicalSSM)

        return response

    def get_smartcard_role_pcse(self) -> str:
        logger.info(
            "starting ssm request to retrieve required smartcard role code pcse"
        )
        params = self.get_ssm_parameters([PCSE_USER_ROLE_CODE])
        response = params.get(PCSE_USER_ROLE_CODE)
        if response is None:
            logger.error(
                LambdaError.LoginPcseSSM.to_str(),
                {"Result": "Unsuccessful login"},
            )
            raise LoginException(500, LambdaError.LoginPcseSSM)
        return response

    def get_org_role_codes(self) -> list[str]:
        logger.info("starting ssm request to retrieve required org roles codes")
        params = self.get_ssm_parameters(
            [
                GP_ORG_ROLE_CODE,
            ]
        )
        response = [params.get(GP_ORG_ROLE_CODE)]
        if None in response:
            logger.error(
                LambdaError.LoginGpODS.to_str(),
                {"Result": "Unsuccessful login"},
            )
            raise LoginException(500, LambdaError.LoginGpODS)
        return response

    def get_org_ods_codes(self) -> list[str]:
        logger.info("starting ssm request to retrieve required org ods codes")
        params = self.get_ssm_parameters(
            [
                PCSE_ODS_CODE,
            ]
        )
        response = [params.get(PCSE_ODS_CODE)]
        if None in response:
            logger.error(
                LambdaError.LoginPcseODS.to_str(),
                {"Result": "Unsuccessful login"},
            )
            raise LoginException(500, LambdaError.LoginPcseODS)
        return response

    def get_jwt_private_key(self) -> list[str]:
        logger.info("starting ssm request to retrieve NDR private key")
        return self.get_ssm_parameter(
            parameter_key="jwt_token_private_key", with_decryption=True
        )
