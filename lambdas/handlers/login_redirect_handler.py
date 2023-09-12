import logging
import os
import time

import boto3
from botocore.exceptions import ClientError
from oauthlib.oauth2 import WebApplicationClient
from utils.lambda_response import ApiGatewayResponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    ssm_parameters_names = ["OIDC_AUTHORISE_URL", "OIDC_CLIENT_ID"]
    ssm_client = boto3.client("ssm", region_name="eu-west-2")
    ssm_response = ssm_client.get_parameters(Names=ssm_parameters_names)
    oidc_parameters = {
        "redirect_uri": os.environ["OIDC_CALLBACK_URL"],
    }
    for parameter in ssm_response["Parameters"]:
        oidc_parameters[parameter["Name"]] = parameter["Value"]
    oidc_client = WebApplicationClient(
        client_id=oidc_parameters["OIDC_CLIENT_ID"],
    )
    location_header, headers, body = oidc_client.prepare_authorization_request(
        authorization_url=oidc_parameters["OIDC_AUTHORISE_URL"],
        redirect_url=os.environ["OIDC_CALLBACK_URL"],
        scope=["openid", "profile", "nationalrbacaccess", "associatedorgs"],
    )
    logger.info(location_header)

    save_state_in_dynamo_db(oidc_client.state)

    headers = {"Location": location_header}

    return ApiGatewayResponse(302, "", "GET").create_api_gateway_response(
        headers=headers
    )


def save_state_in_dynamo_db(state):
    try:
        dynamodb = boto3.resource("dynamodb")
        dynamodb_name = os.environ["AUTH_DYNAMODB_NAME"]
        logger.info(f"Saving state to DynamoDB: {dynamodb_name}")
        table = dynamodb.Table(dynamodb_name)
        table.put_item(
            Item={"state": state, "timeToExist": round(time.time() * 1000) + 60000}
        )
    except ClientError as e:
        logger.error("Unable to connect to DB")
        logger.error(e)
