import logging

from lambdas.utils.lambda_response import ApiGatewayResponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# This is a placeholder handler to make sure we can run our actions before the code is implemented.
def lambda_handler(event, context):
    
    return ApiGatewayResponse(
        204, {} , "GET"
    ).create_api_gateway_response()


