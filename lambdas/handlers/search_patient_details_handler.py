import logging
import os
import json
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
    UserNotAuthorisedException,
)
from utils.lambda_response import ApiGatewayResponse
from utils.decorators.ensure_env_var import ensure_environment_variables
from enums.repository_role import RepositoryRole

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_pds_service():
    return (
        PdsApiService
        if (os.getenv("PDS_FHIR_IS_STUBBED") == "false")
        else MockPdsApiService
    )

@ensure_environment_variables(names=["SSM_PARAM_JWT_TOKEN_PUBLIC_KEY"])
@validate_patient_id
def lambda_handler(event, context):
    logger.info("API Gateway event received - processing starts")
    logger.info(event)

    try:
        ssm_service = SSMService()
        nhs_number = event["queryStringParameters"]["patientId"]
        public_key_location = os.environ["SSM_PARAM_JWT_TOKEN_PUBLIC_KEY"]
        public_key = ssm_service.get_ssm_parameter(public_key_location, True)

        token = event["headers"]["Authorization"]
        decoded = jwt.decode(
            token, public_key, algorithms=["RS256"]
        )

        logger.info(decoded)
        user_ods_code = decoded["selected_organisation"]["org_ods_code"]
        user_role = decoded["repository_role"]
        
        logger.info("Retrieving patient details")
        pds_api_service = get_pds_service()(SSMService())
        patient_details = pds_api_service.fetch_patient_details(nhs_number)

        gp_ods = patient_details.general_practice_ods
        logger.info(f"gp ods: {gp_ods}")
        logger.info(f"length gp ods: {len(gp_ods)}")
        match user_role:
            case RepositoryRole.GP_ADMIN.value:
                # If the GP Admin ods code is null then the patient is not registered.
                # The patient must be registered and registered to the users ODS practise
                if gp_ods == "" or gp_ods != user_ods_code:
                    raise UserNotAuthorisedException
                
            case RepositoryRole.GP_CLINICAL.value:
                # If the GP Clinical ods code is null then the patient is not registered.
                # The patient must be registered and registered to the users ODS practise
                if gp_ods == "" or gp_ods != user_ods_code:
                    raise UserNotAuthorisedException
                
            case RepositoryRole.PCSE:
                # If there is a GP ODS field then the patient is registered, PCSE users should be denied access
                if len(gp_ods) > 0:
                    raise UserNotAuthorisedException
                
            case _:
                raise UserNotAuthorisedException
        

        response = patient_details.model_dump_json(by_alias=True)
        return ApiGatewayResponse(200, response, "GET").create_api_gateway_response()

    except PatientNotFoundException as e:
        logger.error(f"PDS not found: {str(e)}")
        return ApiGatewayResponse(
            404, "Patient does not exist for given NHS number", "GET"
        ).create_api_gateway_response()

    except UserNotAuthorisedException as e:
        logger.error(f"PDS not authorised patient: {str(e)}")
        return ApiGatewayResponse(
            404, "Patient does not exist for given NHS number", "GET"
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
