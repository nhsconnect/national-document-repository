import logging
import os
import time

import boto3
from botocore.exceptions import ClientError
from oauthlib.oauth2 import InsecureTransportError, WebApplicationClient
from services.dynamo_service import DynamoDBService
from utils.lambda_response import ApiGatewayResponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    return prepare_redirect_response(WebApplicationClient)


def prepare_redirect_response(web_application_client_class):
    try:
        ssm_response = get_ssm_parameters()

        oidc_parameters = {
            parameter["Name"]: parameter["Value"]
            for parameter in ssm_response["Parameters"]
        }

        oidc_client = web_application_client_class(
            client_id=oidc_parameters["OIDC_CLIENT_ID"],
        )

        url, _headers, _body = oidc_client.prepare_authorization_request(
            authorization_url=oidc_parameters["OIDC_AUTHORISE_URL"],
            redirect_url=os.environ["OIDC_CALLBACK_URL"],
            scope=["openid", "profile", "nationalrbacaccess", "associatedorgs"],
        )

        save_state_in_dynamo_db(oidc_client.state)

        location_header = {"Location": url}

    except ClientError as e:
        logger.error(f"Error getting using aws client: {e}")
        return ApiGatewayResponse(
            500, "Server error", "GET"
        ).create_api_gateway_response()
    except InsecureTransportError as e:
        logger.error(f"Error preparing auth request: {e}")
        return ApiGatewayResponse(
            500, "Server error", "GET"
        ).create_api_gateway_response()
    return ApiGatewayResponse(302, "", "GET").create_api_gateway_response(
        headers=location_header
    )


def save_state_in_dynamo_db(state):
    dynamodb_name = os.environ["AUTH_DYNAMODB_NAME"]
    dynamodb_service = DynamoDBService()
    ten_minutes = 60 * 10
    ttl = round(time.time()) + ten_minutes
    item = {"State": state, "TimeToExist": ttl}
    dynamodb_service.post_item_service(item=item, table_name=dynamodb_name)


def get_ssm_parameters():
    ssm_parameters_names = ["OIDC_AUTHORISE_URL", "OIDC_CLIENT_ID"]
    ssm_client = boto3.client("ssm")
    return ssm_client.get_parameters(Names=ssm_parameters_names)
