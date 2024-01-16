from typing import Callable

from utils.exceptions import InvalidResourceIdException
from utils.lambda_response import ApiGatewayResponse
from utils.utilities import validate_id


def extract_nhs_number_from_event(event) -> str:
    # Reusable method to get nhs number from event.
    return event["queryStringParameters"]["patientId"]


def validate_patient_id(lambda_func: Callable):
    """A decorator for lambda handler.
    Verify that the incoming event contains a valid patientId (nhs number).
    If not, returns a 400 Bad request response before actual lambda was triggered.

    Usage:
    @validate_patient_id
    def lambda_handler(event, context):
        ...
    """

    def interceptor(event, context):
        try:
            nhs_number = extract_nhs_number_from_event(event)
            validate_id(nhs_number)
        except InvalidResourceIdException:
            return ApiGatewayResponse(
                400, "Invalid NHS number", event["httpMethod"], "VPI_4001"
            ).create_api_gateway_response()
        except KeyError as e:
            return ApiGatewayResponse(
                400,
                f"An error occurred due to missing key: {str(e)}",
                "VPI_4002",
                event["httpMethod"],
            ).create_api_gateway_response()

        # Validation done. Return control flow to original lambda handler
        return lambda_func(event, context)

    return interceptor
