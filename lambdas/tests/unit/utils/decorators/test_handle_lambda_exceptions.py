from botocore.exceptions import ClientError
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.lambda_exceptions import LambdaException
from utils.lambda_response import ApiGatewayResponse


@handle_lambda_exceptions
def lambda_handler(event, context):
    patient_id = event["queryStringParameters"]["patientId"]
    if patient_id == "1234567890":
        raise ClientError({"Error": {"Code": 500, "Message": "test error"}}, "testing")
    if patient_id == "2234567890":
        raise LambdaException(400, "lambda exception")
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

    expected = ApiGatewayResponse(
        500, "Failed to utilise AWS client/resource", "GET", "ERR_AWS_CLIENT"
    ).create_api_gateway_response()
    actual = lambda_handler(test_event, context)

    assert actual == expected


def test_handle_lambda_exceptions_catch_and_handle_lambda_exception(
    valid_id_event, context
):
    test_event = valid_id_event.copy()
    test_event["queryStringParameters"]["patientId"] = "2234567890"

    expected = ApiGatewayResponse(
        400,
        "lambda exception",
        "GET",
    ).create_api_gateway_response()
    actual = lambda_handler(test_event, context)

    assert actual == expected
