import os

from utils.lambda_response import ApiGatewayResponse


def loadEnvironmentVariable(environmentVariableName):
    try:
        return os.environ[environmentVariableName]
    except KeyError:
        return ApiGatewayResponse(
            400, "An error occured processing the required document type", "POST"
        ).create_api_gateway_response()
