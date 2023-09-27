import os

from handlers.lloyd_george_record_stitch_handler import lambda_handler
from utils.lambda_response import ApiGatewayResponse


def test_throws_error_when_no_nhs_number_supplied(missing_id_event, context):
    actual = lambda_handler(missing_id_event, context)
    expected = ApiGatewayResponse(
        400, f"An error occurred due to missing key: 'patientId'", "GET"
    ).create_api_gateway_response()
    assert actual == expected


def test_throws_error_when_environment_variables_not_set(valid_id_event, context):
    actual = lambda_handler(valid_id_event, context)
    expected = ApiGatewayResponse(
        400, f"An error occurred due to missing key: 'LLOYD_GEORGE_DYNAMODB_NAME'", "GET"
    ).create_api_gateway_response()
    assert actual == expected


def test_throws_error_when_nhs_number_not_valid(invalid_id_event, context):
    actual = lambda_handler(invalid_id_event, context)
    expected = ApiGatewayResponse(
        400, f"Invalid NHS number", "GET"
    ).create_api_gateway_response()
    assert actual == expected


def test_throws_error_when_dynamo_service_fails_to_connect(valid_id_event, context):
    os.environ["LLOYD_GEORGE_DYNAMODB_NAME"] = "lg_dynamo"
    os.environ["LLOYD_GEORGE_BUCKET_NAME"] = "lg_bucket"
    actual = lambda_handler(valid_id_event, context)
    expected = ApiGatewayResponse(
        500, f"Unable to retrieve documents for patient 9000000009", "GET"
    ).create_api_gateway_response()
    assert actual == expected
