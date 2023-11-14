from json import JSONDecodeError

from enums.logging_app_interaction import LoggingAppInteraction
from enums.repository_role import RepositoryRole
from pydantic import ValidationError
from services.ssm_service import SSMService
from utils.audit_logging_setup import LoggingService
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.decorators.validate_patient_id import validate_patient_id
from utils.exceptions import (InvalidResourceIdException,
                              PatientNotFoundException, PdsErrorException,
                              UserNotAuthorisedException)
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context
from utils.utilities import get_pds_service

logger = LoggingService(__name__)


@set_request_context_for_logging
@validate_patient_id
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.PATIENT_SEARCH.value

    try:
        nhs_number = event["queryStringParameters"]["patientId"]
        request_context.patient_nhs_no = nhs_number

        user_ods_code = request_context.authorization["selected_organisation"][
            "org_ods_code"
        ]
        user_role = request_context.authorization["repository_role"]

        pds_api_service = get_pds_service()(SSMService())
        patient_details = pds_api_service.fetch_patient_details(nhs_number)

        gp_ods = patient_details.general_practice_ods

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

            case RepositoryRole.PCSE.value:
                # If there is a GP ODS field then the patient is registered, PCSE users should be denied access
                if gp_ods != "":
                    raise UserNotAuthorisedException

            case _:
                raise UserNotAuthorisedException

        logger.audit_splunk_info(
            "Searched for patient details", {"Result": "Patient found"}
        )
        response = patient_details.model_dump_json(by_alias=True)
        return ApiGatewayResponse(200, response, "GET").create_api_gateway_response()

    except PatientNotFoundException as e:
        logger.error(
            f"PDS not found: {str(e)}",
            {"Result": "Patient not found"},
        )
        return ApiGatewayResponse(
            404, "Patient does not exist for given NHS number", "GET"
        ).create_api_gateway_response()

    except UserNotAuthorisedException as e:
        logger.error(
            f"PDS Error: User not authorised: {str(e)}",
            {"Result": "Patient found, User not authorised to view patient"},
        )
        return ApiGatewayResponse(
            404, "Patient does not exist for given NHS number", "GET"
        ).create_api_gateway_response()

    except (InvalidResourceIdException, PdsErrorException) as e:
        logger.error(f"PDS Error: {str(e)}", {"Result": "Patient not found"})
        return ApiGatewayResponse(
            400, "An error occurred while searching for patient", "GET"
        ).create_api_gateway_response()

    except ValidationError as e:
        logger.error(
            f"Failed to parse PDS data:{str(e)}", {"Result": "Patient not found"}
        )
        return ApiGatewayResponse(
            400, "Failed to parse PDS data", "GET"
        ).create_api_gateway_response()

    except JSONDecodeError as e:
        logger.error(
            f"Error while decoding Json:{str(e)}", {"Result": "Patient not found"}
        )
        return ApiGatewayResponse(
            400, "Invalid json in body", "GET"
        ).create_api_gateway_response()

    except KeyError as e:
        logger.error(
            f"Error parsing patientId from json: {str(e)}",
            {"Result": "Patient not found"},
        )
        return ApiGatewayResponse(
            400, "No NHS number found in request parameters.", "GET"
        ).create_api_gateway_response()
