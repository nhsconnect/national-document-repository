import os
import uuid
from urllib.error import HTTPError

import boto3
import requests

env_prefix = os.getenv("SANDBOX")
token = os.getenv("TOKEN")
url = os.getenv("URL")


headers = {
    "content-Type": "application/fhir+json",
    "accept": "application/json",
    "authorization": f"Bearer {token}",
    "x-correlation-id": str(uuid.uuid4()),
}

events = {
    "pds-change-of-gp-1": f"/ndr/{env_prefix}/mns/subscription-id/pds-change-of-gp-1",
    "pds-death-notification-1": f"/ndr/{env_prefix}/mns/subscription-id/pds-death-notification-1",
}

sqs_client = boto3.client("sqs")
sqs_url = sqs_client.get_queue_url(QueueName=f"{env_prefix}-mns-notification-queue")[
    "QueueUrl"
]
sqs_arn = sqs_client.get_queue_attributes(
    QueueUrl=sqs_url, AttributeNames=["QueueArn"]
)["Attributes"]["QueueArn"]

ssm_client = boto3.client("ssm")


def get_subscription_id(event_type):
    request_body = {
        "resourceType": "Subscription",
        "status": "requested",
        "reason": "Integration with the National Document Repository.",
        "criteria": f"eventType={event_type}",
        "channel": {
            "type": "message",
            "endpoint": sqs_arn,
            "payload": "application/json",
        },
    }
    try:
        response = requests.post(url, headers=headers, data=request_body)
        response.raise_for_status()
        id = response.json().get("id")
        return id
    except HTTPError as err:
        print(err)


if __name__ == "__main__":
    for event, parameter in events.items():
        ssm_client.put_parameter(parameter, get_subscription_id(event))
