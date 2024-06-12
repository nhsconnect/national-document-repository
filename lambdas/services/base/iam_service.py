import boto3
from botocore.exceptions import ClientError
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class IAMService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialised = False
        return cls._instance

    def __init__(self):
        if not self.initialised:
            self.sts_client = boto3.client("sts")
            self.initialised = True

    def assume_role(self, assume_role_arn, resource_name, config=None):
        try:
            session_name = resource_name + " " + assume_role_arn.split(":")[-1]
            response = self.sts_client.assume_role(
                RoleArn=assume_role_arn, RoleSessionName=session_name
            )
            temp_credentials = response["Credentials"]
            aws_client = boto3.client(
                resource_name,
                aws_access_key_id=temp_credentials["AccessKeyId"],
                aws_secret_access_key=temp_credentials["SecretAccessKey"],
                aws_session_token=temp_credentials["SessionToken"],
                config=config,
            )
            return aws_client
        except ClientError as error:
            logger.error(
                f"Couldn't assume role {assume_role_arn}"
                f"{error.response['Error']['Message']}"
            )
            raise
