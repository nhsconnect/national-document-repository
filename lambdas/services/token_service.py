import jwt
from botocore.exceptions import ClientError
from services.base.ssm_service import SSMService
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)
ssm_service = SSMService()


class TokenService:
    @staticmethod
    def get_public_key_and_decode_auth_token(auth_token, ssm_public_key_parameter):
        try:
            public_key = ssm_service.get_ssm_parameter(ssm_public_key_parameter, True)
            decoded_token = jwt.decode(auth_token, public_key, algorithms=["RS256"])
            return decoded_token
        except jwt.PyJWTError as e:
            logger.info(f"Failed to decode auth token: {e}")
            return None
        except ClientError as e:
            logger.info(f"Failed to retrieve auth token: {e}")
            return None
