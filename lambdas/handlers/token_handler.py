import json
import logging

import boto3
import botocore
import jwt
import time
from utils.lambda_response import ApiGatewayResponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """Do not print the auth token unless absolutely necessary """
    print(f"incoming event: {event}")
    try:
        client = boto3.client('ssm')
        logger.info("starting ssm request")
        ssm_response = client.get_parameter(
        Name='jwt_token_private_key',
        WithDecryption=True
        )
        logger.info("ending ssm request")
        cis2_user_info = event['body']['user']
        cis2_user_info['exp'] = time.time() + 60*15
        cis2_user_info['iss'] = "nhs repo"
        private_key = ssm_response['Parameter']['Value']
        logger.info("starting encoding request")
        token = jwt.encode(cis2_user_info, private_key, algorithm="RS256")
        logger.info(f"encoded JWT: {token}")
    except botocore.exceptions.ClientError as e:
        logger.error(e)
        return ApiGatewayResponse(400, f"{str(e)}", "GET").create_api_gateway_response()
    except jwt.PyJWTError as e:
        logger.info(f"error while encoding JWT: {e}")
        return ApiGatewayResponse(400, f"{str(e)}", "GET").create_api_gateway_response()
    except (KeyError, TypeError) as e:
        logger.error(e)
        return ApiGatewayResponse(400, f"{str(e)}", "GET").create_api_gateway_response()

    response = {
    "access_token": token,
    "token_type": "Bearer",
    "expires_in": 3600,
  }

    return ApiGatewayResponse(200, json.dumps(response), "GET").create_api_gateway_response()