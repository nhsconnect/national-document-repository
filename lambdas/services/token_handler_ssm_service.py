import logging

from services.ssm_service import SSMService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TokenHandlerSSMService(SSMService):

    def __init__(self):
        super().__init__()

    def get_role_codes(self):
        logger.info("starting ssm request to retrieve required role codes")
        return self.get_ssm_parameters([
            "ods_code_pcse",
            "role_code_gpadmin",
            "role_code_gpp_org",
            "role_code_pcse",
        ])

    def get_jwt_private_key(self):
        logger.info("starting ssm request to retrieve NDR private key")
        return self.get_ssm_parameter(
            parameter_key="jwt_token_private_key", with_decryption=True
        )
