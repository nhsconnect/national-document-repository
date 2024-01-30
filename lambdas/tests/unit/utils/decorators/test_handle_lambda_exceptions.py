import json
from enum import Enum

from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.lambda_exceptions import LambdaException
from utils.lambda_response import ApiGatewayResponse


class MockError(Enum):
    ErrorClient = {
        "message": "Client error",
        "err_code": "AB_XXXX",
        "interaction_id": "88888888-4444-4444-4444-121212121212",
    }
    ErrorKey = {
        "message": "Key error",
        "err_code": "CD_XXXX",
        "interaction_id": "88888888-4444-4444-4444-121212121212",
    }


@handle_lambda_exceptions
def lambda_handler(event, context):
    patient_id = event["queryStringParameters"]["patientId"]
    if patient_id == "1234567890":
        error = MockError.ErrorClient
        raise LambdaException(400, error)
    if patient_id == "2234567890":
        error = MockError.ErrorKey
        raise LambdaException(400, error)
    return ApiGatewayResponse(200, "OK", "GET").create_api_gateway_response()


def test_handle_lambda_exceptions_does_nothing_when_no_exception_is_raised(
    valid_id_event, context
):
    expected = ApiGatewayResponse(200, "OK", "GET").create_api_gateway_response()
    actual = lambda_handler(valid_id_event, context)

    assert actual == expected


def test_handle_lambda_exceptions_catch_and_handle_client_error(
    valid_id_event, context
):
    test_event = valid_id_event.copy()
    test_event["queryStringParameters"]["patientId"] = "1234567890"
    body = json.dumps(MockError.ErrorClient.value)
    expected = ApiGatewayResponse(
        400,
        body,
        "GET",
    ).create_api_gateway_response()
    actual = lambda_handler(test_event, context)

    assert actual == expected


def test_handle_lambda_exceptions_catch_and_handle_lambda_exception(
    valid_id_event, context
):
    test_event = valid_id_event.copy()
    test_event["queryStringParameters"]["patientId"] = "2234567890"
    body = json.dumps(MockError.ErrorKey.value)
    expected = ApiGatewayResponse(
        400,
        body,
        "GET",
    ).create_api_gateway_response()
    actual = lambda_handler(test_event, context)

    assert actual == expected
