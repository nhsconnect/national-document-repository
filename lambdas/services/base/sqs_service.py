import uuid

import boto3
from botocore.client import Config as BotoConfig


class SQSService:
    def __init__(self, *args, **kwargs):
        config = BotoConfig(retries={"max_attempts": 3, "mode": "standard"})
        self.client = boto3.client("sqs", config=config)
        super().__init__(*args, **kwargs)

    def send_message_fifo(self, queue_url: str, message_body: str, group_id: str):
        self.client.send_message(
            QueueUrl=queue_url, MessageBody=message_body, MessageGroupId=group_id
        )

    def send_message_standard(self, queue_url: str, message_body: str):
        self.client.send_message(QueueUrl=queue_url, MessageBody=message_body)

    def send_message_batch_standard(self, queue_url: str, messages: list[str]):
        base_delay = 150
        entries = []
        for i, body in enumerate(messages):
            delay = base_delay
            entries.append(
                {
                    "Id": str(uuid.uuid4()),
                    "MessageBody": body,
                    "DelaySeconds": delay,
                }
            )

        response = self.client.send_message_batch(
            QueueUrl=queue_url,
            Entries=entries,
        )

        if "Failed" in response and response["Failed"]:
            failed_ids = [f["Id"] for f in response["Failed"]]
            failed_messages = [
                entry["MessageBody"] for entry in entries if entry["Id"] in failed_ids
            ]
            error_msg = (
                f"Some messages failed to send. Failed IDs: {failed_ids}. "
                f"Failed message bodies: {failed_messages}"
            )
            raise Exception(error_msg)

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
        group_id: str,
    ):
        self.client.send_message(
            QueueUrl=queue_url,
            MessageAttributes={
                "NhsNumber": {"DataType": "String", "StringValue": nhs_number},
            },
            MessageBody=message_body,
            MessageGroupId=group_id,
        )
