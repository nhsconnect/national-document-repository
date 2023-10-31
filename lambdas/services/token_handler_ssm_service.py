import logging

from services.ssm_service import SSMService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TokenHandlerSSMService(SSMService):

    def __init__(self):
        super().__init__()

    def get_smartcard_role_codes(self):
        logger.info("starting ssm request to retrieve required smartcard role codes")
        params = self.get_ssm_parameters([
            "/auth/smartcard/role/gp_admin",
            "/auth/smartcard/role/gp_clinical",
            "/auth/smartcard/role/pcse",
        ])

        logger.info(f"smartcard role params: {params}")
        return params
    
    def get_org_role_codes(self):
        logger.info("starting ssm request to retrieve required org roles codes")
        params = self.get_ssm_parameters([
            "/auth/org/role_code/gpp",
        ])

        logger.info(f"role code params: {params}")
        return params

    def get_org_ods_codes(self):
        logger.info("starting ssm request to retrieve required org ods codes")
        params = self.get_ssm_parameters([
            "/auth/org/ods_code/pcse",
        ])

        logger.info(f"org ods params: {params}")
        return params

    def get_jwt_private_key(self):
        logger.info("starting ssm request to retrieve NDR private key")
        return self.get_ssm_parameter(
            parameter_key="jwt_token_private_key", with_decryption=True
        )
