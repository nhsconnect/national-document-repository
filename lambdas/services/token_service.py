import jwt
from botocore.exceptions import ClientError
from services.base.ssm_service import SSMService

ssm_service = SSMService()


class TokenService:
    @staticmethod
    def get_public_key_and_decode_auth_token(auth_token, ssm_public_key_parameter):
        try:
            public_key = ssm_service.get_ssm_parameter(ssm_public_key_parameter, True)
            decoded_token = jwt.decode(auth_token, public_key, algorithms=["RS256"])
            return decoded_token
        except (jwt.PyJWTError, ClientError):
            return None
