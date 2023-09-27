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
