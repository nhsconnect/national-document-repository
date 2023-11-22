import jwt
from botocore.exceptions import ClientError


class TokenService:
    def __init__(self, ssm_service):
        self.ssm_service = ssm_service

    def get_public_key_and_decode_auth_token(
        self, auth_token, ssm_public_key_parameter
    ):
        try:
            public_key = self.ssm_service.get_ssm_parameter(
                ssm_public_key_parameter, True
            )
            decoded_token = jwt.decode(auth_token, public_key, algorithms=["RS256"])
            return decoded_token
        except (jwt.PyJWTError, ClientError):
            return None
