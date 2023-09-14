import json
import logging

from services.ods_api_service import OdsApiService
from services.oidc_service import OidcService
from utils.exceptions import AuthorisationException
from utils.lambda_response import ApiGatewayResponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    try:
        auth_code = event["queryStringParameters"]["code"]
    except KeyError:
        return ApiGatewayResponse(
            400, "Please supply an authorisation code", "GET"
        ).create_api_gateway_response()

    try:
        oidc_service = OidcService()

        logger.info("Fetching access token from OIDC Provider")
        access_token, id_token_claim_set = oidc_service.fetch_tokens(auth_code)

        logger.info("Use the access token to fetch user's organisation codes")
        org_codes = oidc_service.fetch_user_org_codes(access_token)

        permitted_orgs_and_roles = OdsApiService.fetch_organisation_with_permitted_role(org_codes)
        if len(permitted_orgs_and_roles) == 0:
            logger.info("User has no valid organisations to log in")
            raise AuthorisationException('No valid organisations for user')

        # create session after all verifications done
        # issue Authorization token
        authorization_token = 'place_holder'

        response = {"organisations": org_codes, "authorization_token": authorization_token}

    except AuthorisationException:
        return ApiGatewayResponse(
            401, "Failed to authenticate user with OIDC service", "GET"
        ).create_api_gateway_response()

    return ApiGatewayResponse(
        200, json.dumps(response), "GET"
    ).create_api_gateway_response()

    # COMMENT OUT the logic for JWT signing for the moment
    # try:
    #     client = boto3.client("ssm")
    #     logger.info("starting ssm request")
    #     ssm_response = client.get_parameter(
    #         Name="jwt_token_private_key", WithDecryption=True
    #     )
    #     logger.info("ending ssm request")
    #     cis2_user_info = event["body"]["user"]
    #     cis2_user_info["exp"] = time.time() + 60 * 15
    #     cis2_user_info["iss"] = "nhs repo"
    #     private_key = ssm_response["Parameter"]["Value"]
    #     logger.info("starting encoding request")
    #     token = jwt.encode(cis2_user_info, private_key, algorithm="RS256")
    #     logger.info(f"encoded JWT: {token}")
    # except botocore.exceptions.ClientError as e:
    #     logger.error(e)
    #     return ApiGatewayResponse(400, f"{str(e)}", "GET").create_api_gateway_response()
    # except jwt.PyJWTError as e:
    #     logger.info(f"error while encoding JWT: {e}")
    #     return ApiGatewayResponse(400, f"{str(e)}", "GET").create_api_gateway_response()
    # except (KeyError, TypeError) as e:
    #     logger.error(e)
    #     return ApiGatewayResponse(400, f"{str(e)}", "GET").create_api_gateway_response()
    #
    # response = {
    #     "access_token": token,
    #     "token_type": "Bearer",
    #     "expires_in": 3600,
    # }
    #
