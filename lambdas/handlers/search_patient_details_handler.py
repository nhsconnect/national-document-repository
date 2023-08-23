import logging
from json import JSONDecodeError

from pydantic import ValidationError
from services.pds_api_service import PdsApiService
from utils.exceptions import (InvalidResourceIdException,
                              PatientNotFoundException, PdsErrorException)
from utils.lambda_response import ApiGatewayResponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info("API Gateway event received - processing starts")
    logger.info(event)

    try:
        nhs_number = event["queryStringParameters"]["patientId"]

        logger.info("Retrieving patient details")
        pds_api_service = PdsApiService()

        patient_details = pds_api_service.fetch_patient_details(nhs_number)
        response = patient_details.model_dump_json(by_alias=True)

        return ApiGatewayResponse(200, response, "GET").create_api_gateway_response()

    except PatientNotFoundException as e:
        return ApiGatewayResponse(404, f"{str(e)}", "GET").create_api_gateway_response()

    except InvalidResourceIdException as e:
        return ApiGatewayResponse(400, f"{str(e)}", "GET").create_api_gateway_response()

    except PdsErrorException as e:
        return ApiGatewayResponse(400, f"{str(e)}", "GET").create_api_gateway_response()

    except ValidationError as e:
        return ApiGatewayResponse(
            400, f"Failed to parse PDS data: {str(e)}", "GET"
        ).create_api_gateway_response()

    except JSONDecodeError as e:
        return ApiGatewayResponse(
            400, f"Invalid json in body: {str(e)}", "GET"
        ).create_api_gateway_response()

    except KeyError as e:
        logger.info(f"Error parsing patientId from json: {str(e)}")
        return ApiGatewayResponse(
            400, "No NHS number found in request parameters.", "GET"
        ).create_api_gateway_response()
