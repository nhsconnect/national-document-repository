import logging
import os
import time

import boto3
from botocore.exceptions import ClientError
from oauthlib.oauth2 import WebApplicationClient, InsecureTransportError
from utils.lambda_response import ApiGatewayResponse
from services.dynamo_services import DynamoDBService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    try:
        ssm_parameters_names = ["OIDC_AUTHORISE_URL", "OIDC_CLIENT_ID"]
        ssm_client = boto3.client("ssm", region_name="eu-west-2")
        ssm_response = ssm_client.get_parameters(Names=ssm_parameters_names)

        oidc_parameters = {parameter["Name"] : parameter["Value"] for parameter in ssm_response["Parameters"]}

        oidc_client = WebApplicationClient(
            client_id=oidc_parameters["OIDC_CLIENT_ID"],
        )

        url, headers, body = oidc_client.prepare_authorization_request(
            authorization_url=oidc_parameters["OIDC_AUTHORISE_URL"],
            redirect_url=os.environ["OIDC_CALLBACK_URL"],
            scope=["openid", "profile", "nationalrbacaccess", "associatedorgs"],
        )
        save_state_in_dynamo_db(oidc_client.state)

        location_header = {"Location": url}
    except ClientError as e:
        logger.error(f"Error getting using aws client: {e}")
        return ApiGatewayResponse(500, e, "GET").create_api_gateway_response()
    except InsecureTransportError as e:
        logger.error(f"Error preparing auth request: {e}")
        return ApiGatewayResponse(500, e, "GET").create_api_gateway_response()
    return ApiGatewayResponse(302, "", "GET").create_api_gateway_response(
        headers=location_header
    )

def save_state_in_dynamo_db(state):
    dynamodb_name = os.environ["AUTH_DYNAMODB_NAME"]
    dynamodb_service = DynamoDBService(dynamodb_name)
    ttl = round(time.time()) + 60 * 10
    item = {"State": state, "TimeToExist": ttl}
    dynamodb_service.post_item_service(item=item)
