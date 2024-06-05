import boto3
from botocore.exceptions import ClientError


class IAMService:
    def __init__(self):
        self.sts_client = boto3.client("sts")

    def assume_role(self, assume_role_arn, resource_name, config=None):
        try:
            response = self.sts_client.assume_role(RoleArn=assume_role_arn)
            temp_credentials = response["Credentials"]
            aws_client = boto3.client(
                resource_name,
                aws_access_key_id=temp_credentials["AccessKeyId"],
                aws_secret_access_key=temp_credentials["SecretAccessKey"],
                aws_session_token=temp_credentials["SessionToken"],
                config=config,
            )
            print(f"Assumed role {assume_role_arn} and got temporary credentials.")
            return aws_client
        except ClientError as error:
            print(
                f"Couldn't assume role {assume_role_arn}. Here's why: "
                f"{error.response['Error']['Message']}"
            )
            raise
