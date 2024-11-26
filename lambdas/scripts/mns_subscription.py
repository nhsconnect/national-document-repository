import os
import uuid

import boto3
import requests

env_prefix = os.getenv("SANDBOX")
token = os.getenv("TOKEN")

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

url = "https://sandbox.api.service.nhs.uk/multicast-notification-service/subscriptions"

sqs = boto3.client("sqs")
sqs_url = sqs.get_queue_url(QueueName=f"{env_prefix}-mns-notification-queue")[
    "QueueUrl"
]
sqs_arn = sqs.get_queue_attributes(QueueUrl=sqs_url, AttributeNames=["QueueArn"])[
    "Attributes"
]["QueueArn"]

ssm = boto3.client("ssm")


def get_subscription_id(event_type):
    request_body = {
        "resourceType": "Subscription",
        "status": "requested",
        "end": "2022-04-05T17:31:00.000Z",
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
        id = response.json().get("id")
        return id
    except requests.exceptions.RequestException as e:
        print(e)


if __name__ == "__main__":

    for event, parameter in events.items():
        ssm.put_parameter(parameter, get_subscription_id(event))
