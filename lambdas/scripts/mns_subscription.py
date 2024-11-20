# get subscription endpoints, ping them, visit the response URL
# create an ssm_parameter for each subscription id from each response
# ndr/{env}/mns/subscription_id/pds-change-of-gp-1
# ndr/{env}/mns/subscription_id/pds-death-notification-1
import os

# # how do i get the env?
# import uuid
#
# # what do I need to be able to do this,
# # ssm_service, put... and get...
# # need to know env, how does that work? how do I get it, os.getenv?
# # need an auth service to get the bearer token.
#
# import boto3
# import requests
# from enums.pds_ssm_parameters import SSMParameter
# from services.base.nhs_oauth_service import NhsOauthService
# from services.base.ssm_service import SSMService
#
#
# ENV = 'ndrb'
# QUEUE = f"arn:aws:sqs:eu-west-2:account number:{ENV}-mns-subscription-queue"
# ssm_service = SSMService()
# oauth_service = NhsOauthService(ssm_service)
#
# headers = {
#     "content-Type": "application/fhir+json",
#     "accept": "application/json",
#     "authorization": f"Bearer {oauth_service.get_active_access_token()}",
#     "x-correlation-id": str(uuid.uuid4())
# }
#
# events = {
#     "pds-change-of-gp-1": f"/ndr/{ENV}/mns/subscription-id/pds-change-of-gp-1",
#     "pds-death-notification-1": f"/ndr/{ENV}/mns/subscription-id/pds-death-notification-1"
# }
#
# url = "https://sandbox.api.service.nhs.uk/multicast-notification-service/subscriptions"
#
# def get_subscription_id(event_type,):
#     request_body = {
#         "resourceType": "Subscription",
#         "status": "requested",
#         "end": "2022-04-05T17:31:00.000Z",
#         "reason": "A description of why this subscription should be created.",
#         "criteria": f"eventType={event_type}",
#         "channel": {
#             "type": "message",
#             "endpoint": QUEUE,
#             "payload": "application/json"
#         }
#     }
#     try:
#         response = requests.post(url, headers=headers, data=request_body)
#         id = response.json().get('id')
#         return id
#
#     except requests.exceptions.RequestException as e:
#         print(e)
#
# for event, parameter in events.items():
#     ssm_service.update_ssm_parameter(parameter, get_subscription_id(event))

# needs third value, securestring?

if __name__ == "__main__":
    env = os.getenv("ENV")
    print(env)
