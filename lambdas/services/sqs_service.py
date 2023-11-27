import boto3
from botocore.client import Config as BotoConfig


class SQSService:
    def __init__(self, *args, **kwargs):
        config = BotoConfig(retries={"max_attempts": 3, "mode": "standard"})
        self.client = boto3.client("sqs", config=config)
        super().__init__(*args, **kwargs)

    def send_message_standard(self, queue_url: str, message_body: str):
        self.client.send_message(QueueUrl=queue_url, MessageBody=message_body)

    def send_message_with_attr(
        self, queue_url: str, message_body: str, attributes: dict
    ):
        self.client.send_message(
            QueueUrl=queue_url, MessageBody=message_body, MessageAttributes=attributes
        )

    def send_message_with_nhs_number_attr_fifo(
        self,
        queue_url: str,
        message_body: str,
        nhs_number: str,
        delay_seconds: int = 0,
        group_id=str,
    ):
        self.client.send_message(
            QueueUrl=queue_url,
            MessageAttributes={
                "NhsNumber": {"DataType": "String", "StringValue": nhs_number},
            },
            MessageBody=message_body,
            DelaySeconds=delay_seconds,
            MessageGroupId=group_id,
        )
