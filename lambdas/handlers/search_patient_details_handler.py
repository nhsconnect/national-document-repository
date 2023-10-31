import logging
import os
from json import JSONDecodeError

import boto3
import jwt
from pydantic import ValidationError
from services.mock_pds_service import MockPdsApiService
from services.pds_api_service import PdsApiService
from services.ssm_service import SSMService
from utils.decorators.validate_patient_id import validate_patient_id
from utils.exceptions import (
    InvalidResourceIdException,
    PatientNotFoundException,
    PdsErrorException,
    PatientNotAuthorisedException,
)
from utils.lambda_response import ApiGatewayResponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_pds_service():
    return (
        PdsApiService
        if (os.getenv("PDS_FHIR_IS_STUBBED") == "false")
        else MockPdsApiService
    )


@validate_patient_id
def lambda_handler(event, context):
    logger.info("API Gateway event received - processing starts")
    logger.info(event)

    try:
        nhs_number = event["queryStringParameters"]["patientId"]
        client = boto3.client("ssm")
        ssm_public_key_parameter_name = os.environ["SSM_PARAM_JWT_TOKEN_PUBLIC_KEY"]
        ssm_response = client.get_parameter(
            Name=ssm_public_key_parameter_name, WithDecryption=True
        )
        public_key = ssm_response["Parameter"]["Value"]

        decoded = jwt.decode(
            event["authorizationToken"], public_key, algorithms=["RS256"]
        )

        user_ods_codes = [ods["ods_code"] for ods in decoded["organisations"]]

        logger.info("Retrieving patient details")
        pds_api_service = get_pds_service()(SSMService())
        patient_details = pds_api_service.fetch_patient_details(nhs_number)
        if patient_details.general_practice_ods not in user_ods_codes:
            raise PatientNotAuthorisedException

        response = patient_details.model_dump_json(by_alias=True)

        return ApiGatewayResponse(200, response, "GET").create_api_gateway_response()

    except PatientNotFoundException as e:
        logger.error(f"PDS not found: {str(e)}")
        return ApiGatewayResponse(
            404, "Patient does not exist for given NHS number", "GET"
        ).create_api_gateway_response()

    except PatientNotAuthorisedException as e:
        logger.error(f"PDS not authorised patient: {str(e)}")
        return ApiGatewayResponse(
            404, "Patient is outside of your access policy", "GET"
        ).create_api_gateway_response()

    except (InvalidResourceIdException, PdsErrorException) as e:
        logger.error(f"PDS Error: {str(e)}")
        return ApiGatewayResponse(
            400, "An error occurred while searching for patient", "GET"
        ).create_api_gateway_response()

    except ValidationError as e:
        logger.error(f"Failed to parse PDS data:{str(e)}")
        return ApiGatewayResponse(
            400, "Failed to parse PDS data", "GET"
        ).create_api_gateway_response()

    except JSONDecodeError as e:
        logger.error(f"Error while decoding Json:{str(e)}")
        return ApiGatewayResponse(
            400, "Invalid json in body", "GET"
        ).create_api_gateway_response()

    except KeyError as e:
        logger.error(f"Error parsing patientId from json: {str(e)}")
        return ApiGatewayResponse(
            400, "No NHS number found in request parameters.", "GET"
        ).create_api_gateway_response()
