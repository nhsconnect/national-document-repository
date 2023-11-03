from json import JSONDecodeError

from pydantic import ValidationError
from services.ssm_service import SSMService
from utils.audit_logging_setup import LoggingService
from utils.decorators.validate_patient_id import validate_patient_id
from utils.exceptions import (
    InvalidResourceIdException,
    PatientNotFoundException,
    PdsErrorException,
)
from utils.lambda_response import ApiGatewayResponse
from utils.utilities import get_pds_service

from utils.decorators.set_audit_arg import set_request_context_for_logging

logger = LoggingService(__name__)


@set_request_context_for_logging
@validate_patient_id
def lambda_handler(event, context):
    logger.info("API Gateway event received - processing starts")

    try:
        nhs_number = event["queryStringParameters"]["patientId"]

        logger.info("Retrieving patient details")
        pds_api_service = get_pds_service()(SSMService())
        patient_details = pds_api_service.fetch_patient_details(nhs_number)
        response = patient_details.model_dump_json(by_alias=True)
        logger.audit_splunk_info(
            "Searched for patient details", {"nhsNumber": nhs_number}
        )

        return ApiGatewayResponse(200, response, "GET").create_api_gateway_response()

    except PatientNotFoundException as e:
        logger.error(f"PDS not found: {str(e)}")
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
