from typing import Callable

from enums.lambda_error import LambdaError
from utils.audit_logging_setup import LoggingService
from utils.exceptions import InvalidResourceIdException
from utils.lambda_response import ApiGatewayResponse
from utils.utilities import validate_nhs_number

logger = LoggingService(__name__)


def extract_nhs_number_from_event(event) -> str:
    # Reusable method to get nhs number from the event.
    querystring = event.get("queryStringParameters")
    if querystring is None:
        raise KeyError
    return querystring["patientId"]


def validate_patient_id(lambda_func: Callable):
    """A decorator for lambda handler.
    Verify that the incoming event contains a valid patientId (nhs number).
    If not, returns a 400 Bad request response before the actual lambda was triggered.

    Usage:
    @validate_patient_id
    def lambda_handler(event, context):
        ...
    """

    def interceptor(event, context):
        nhs_number = ""
        try:
            nhs_number = extract_nhs_number_from_event(event)
            validate_nhs_number(nhs_number)
        except InvalidResourceIdException as e:
            logger.error(
                f"{LambdaError.PatientIdInvalid.to_str()}: {str(e)}",
                {"Result": f"Invalid patient number {nhs_number}"},
            )
            return ApiGatewayResponse(
                400,
                LambdaError.PatientIdInvalid.create_error_body({"number": nhs_number}),
                event["httpMethod"],
            ).create_api_gateway_response()
        except KeyError as e:
            logger.error(
                f"{LambdaError.PatientIdNoKey.to_str()}: {str(e)}",
                {"Result": "An error occurred due to missing key"},
            )
            return ApiGatewayResponse(
                400,
                LambdaError.PatientIdNoKey.create_error_body(),
                event["httpMethod"],
            ).create_api_gateway_response()

        # Validation done. Return control flow to original lambda handler
        return lambda_func(event, context)

    return interceptor


def validate_patient_id_fhir(lambda_func: Callable):
    """A decorator for lambda handler.
    Verify that the incoming event contains a valid subject:identifier (nhs number).
    If not, returns a 400 Bad request response before the actual lambda was triggered in a fhir format.

    Usage:
    @validate_patient_id
    def lambda_handler(event, context):
        ...
    """

    def interceptor(event, context):
        nhs_number = ""
        try:
            querystring = event.get("queryStringParameters")
            if querystring is None:
                raise KeyError
            subject_identifier = querystring["subject:identifier"]
            nhs_number = subject_identifier.split("|")[-1]
            validate_nhs_number(nhs_number)
        except InvalidResourceIdException as e:
            logger.error(
                f"{LambdaError.PatientIdInvalid.to_str()}: {str(e)}",
                {"Result": f"Invalid patient number {nhs_number}"},
            )
            return ApiGatewayResponse(
                status_code=400,
                body=LambdaError.PatientIdInvalid.create_error_response(
                    {"number": nhs_number}
                ).create_error_fhir_response(
                    LambdaError.PatientIdInvalid.value.get("fhir_coding")
                ),
                methods=event["httpMethod"],
            ).create_api_gateway_response()

        except (KeyError, IndexError) as e:
            logger.error(
                f"{LambdaError.PatientIdNoKey.to_str()}: {str(e)}",
                {"Result": "An error occurred due to missing key"},
            )
            return ApiGatewayResponse(
                status_code=400,
                body=LambdaError.PatientIdNoKey.create_error_response().create_error_fhir_response(
                    LambdaError.PatientIdNoKey.value.get("fhir_coding")
                ),
                methods=event["httpMethod"],
            ).create_api_gateway_response()
        # Validation done. Return control flow to the original lambda handler
        return lambda_func(event, context)

    return interceptor
