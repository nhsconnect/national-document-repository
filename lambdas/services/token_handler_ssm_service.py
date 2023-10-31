import logging

from services.ssm_service import SSMService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TokenHandlerSSMService(SSMService):

    def __init__(self):
        super().__init__()

    def get_smartcard_role_codes(self):
        logger.info("starting ssm request to retrieve required smartcard role codes")
        return self.get_ssm_parameters([
            "/auth/smartcard/role/gp_admin",
            "/auth/smartcard/role/gp_clinical",
            "/auth/smartcard/role/pcse",
        ])
    
    def get_org_role_codes(self):
        logger.info("starting ssm request to retrieve required smartcard role codes")
        return self.get_ssm_parameters([
            "/auth/org/role_code/gpp",
        ])

    def get_org_ods_codes(self):
        logger.info("starting ssm request to retrieve required smartcard role codes")
        return self.get_ssm_parameters([
            "/auth/org/ods_code/pcse",
        ])

    def get_jwt_private_key(self):
        logger.info("starting ssm request to retrieve NDR private key")
        return self.get_ssm_parameter(
            parameter_key="jwt_token_private_key", with_decryption=True
        )
