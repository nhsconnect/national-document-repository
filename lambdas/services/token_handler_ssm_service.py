import logging

from services.ssm_service import SSMService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TokenHandlerSSMService(SSMService):
    def __init__(self):
        super().__init__()

    def get_smartcard_role_codes(self) -> list[str]:
        logger.info("starting ssm request to retrieve required smartcard role codes")
        params = self.get_ssm_parameters(
            [
                "/auth/smartcard/role/gp_admin",
                "/auth/smartcard/role/gp_clinical",
                "/auth/smartcard/role/pcse",
            ]
        )

        response = [
            params["/auth/smartcard/role/gp_admin"],
            params["/auth/smartcard/role/gp_clinical"],
            params["/auth/smartcard/role/pcse"],
        ]

        return response

    def get_smartcard_role_gp_admin(self) -> str:
        logger.info(
            "starting ssm request to retrieve required smartcard role code gp admin"
        )
        params = self.get_ssm_parameters(["/auth/smartcard/role/gp_admin"])

        response = params["/auth/smartcard/role/gp_admin"]
        return response

    def get_smartcard_role_gp_clinical(self) -> str:
        logger.info(
            "starting ssm request to retrieve required smartcard role code gp clinical"
        )
        params = self.get_ssm_parameters(["/auth/smartcard/role/gp_clinical"])

        logger.info(f"Params: {params}")
        response = params["/auth/smartcard/role/gp_clinical"]
        return response

    def get_smartcard_role_pcse(self) -> str:
        logger.info(
            "starting ssm request to retrieve required smartcard role code pcse"
        )
        params = self.get_ssm_parameters(["/auth/smartcard/role/pcse"])

        response = params["/auth/smartcard/role/pcse"]
        return response

    def get_org_role_codes(self) -> list[str]:
        logger.info("starting ssm request to retrieve required org roles codes")
        params = self.get_ssm_parameters(
            [
                "/auth/org/role_code/gpp",
            ]
        )

        response = [params["/auth/org/role_code/gpp"]]
        return response

    def get_org_ods_codes(self) -> list[str]:
        logger.info("starting ssm request to retrieve required org ods codes")
        params = self.get_ssm_parameters(
            [
                "/auth/org/ods_code/pcse",
            ]
        )

        response = [params["/auth/org/ods_code/pcse"]]
        return response

    def get_jwt_private_key(self) -> list[str]:
        logger.info("starting ssm request to retrieve NDR private key")
        return self.get_ssm_parameter(
            parameter_key="jwt_token_private_key", with_decryption=True
        )
