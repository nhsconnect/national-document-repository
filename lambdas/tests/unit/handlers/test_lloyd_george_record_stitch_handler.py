from handlers.lloyd_george_record_stitch_handler import lambda_handler
from utils.lambda_response import ApiGatewayResponse

MISSING_NHS_NUMBER_KEY_ERROR = ApiGatewayResponse(
    400, f"An error occurred due to missing key: 'patientId'", "GET"
).create_api_gateway_response()


def test_throws_error_when_no_nhs_number_supplied(missing_id_event, context):
    actual = lambda_handler(missing_id_event, context)
    expected = MISSING_NHS_NUMBER_KEY_ERROR
    assert actual == expected
