import os
import uuid
from urllib.error import HTTPError

import boto3
import requests
from services.base.nhs_oauth_service import NhsOauthService
from services.base.ssm_service import SSMService

env_prefix = os.getenv("SANDBOX")
url = os.getenv("URL")

ssm_service = SSMService()
auth_service = NhsOauthService(ssm_service)


headers = {
    "authorization": f"Bearer {auth_service.get_active_access_token()}",
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
        response = requests.post(url, headers=headers, json=request_body)
        response.raise_for_status()
        subscription_id = response.json().get("id")
        return subscription_id
    except HTTPError as err:
        print(err)


if __name__ == "__main__":
    for event, parameter in events.items():
        subscription_id = get_subscription_id(event)
        ssm_service.update_ssm_parameter(
            parameter_key=parameter,
            parameter_value=subscription_id,
            parameter_type="SecureString",
        )
