import os

import boto3

from lambdas.utils.lambda_response import ApiGatewayResponse


def lambda_handler(event, context):

    ssm_parameters_names = ["OIDC_AUTHORISE_URL", "OIDC_CLIENT_ID"]
    client = boto3.client("ssm", region_name="eu-west-2")
    ssm_response = client.get_parameters(
        Names=ssm_parameters_names
    )
    oidc_parameters = {'redirect_uri': os.environ["OIDC_CALLBACK_URL"],
                       'response_type': 'code',
                       'scope': ["openid", "profile", "nationalrbacaccess", "associatedorgs"]}
    for parameter in ssm_response['Parameters']:
        oidc_parameters[parameter['Name']] = parameter['Value']
    headers = {"Location" : f"{oidc_parameters['OIDC_AUTHORISE_URL']}?"
                            f"response_type={oidc_parameters['response_type']}&"
                            f"scope={oidc_parameters['scope']}&"
                            f"client_id={oidc_parameters['OIDC_CLIENT_ID']}&"
                            f"state=&"
                            f"redirect_uri={oidc_parameters['redirect_uri']}"}

    return ApiGatewayResponse(
        302, "", "GET", headers=headers
    ).create_api_gateway_response()

