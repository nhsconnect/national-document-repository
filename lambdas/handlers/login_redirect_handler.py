import logging
import os

from oauthlib.oauth2 import WebApplicationClient
import boto3

from utils.lambda_response import ApiGatewayResponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)
def lambda_handler(event, context):

    ssm_parameters_names = ["OIDC_AUTHORISE_URL", "OIDC_CLIENT_ID"]
    client = boto3.client("ssm", region_name="eu-west-2")
    ssm_response = client.get_parameters(
        Names=ssm_parameters_names
    )
    oidc_parameters = {'redirect_uri': os.environ["OIDC_CALLBACK_URL"],
                       }
    for parameter in ssm_response['Parameters']:
        oidc_parameters[parameter['Name']] = parameter['Value']
    client = WebApplicationClient(
            client_id=oidc_parameters['OIDC_CLIENT_ID'],
        )
    location_header, headers, body = client.prepare_authorization_request(
    authorization_url=oidc_parameters['OIDC_AUTHORISE_URL'],
    redirect_url=os.environ["OIDC_CALLBACK_URL"],
    scope=["openid", "profile", "nationalrbacaccess", "associatedorgs"],
    )
    logger.info(location_header)

    headers = {"Location" : location_header}

    return ApiGatewayResponse(
        302, "", "GET"
    ).create_api_gateway_response(headers=headers)
