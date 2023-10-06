from unittest.mock import MagicMock

from utils.decorators.validate_patient_id import validate_patient_id
from utils.lambda_response import ApiGatewayResponse

actual_lambda_logic = MagicMock()


@validate_patient_id
def lambda_handler(event, _context):
    actual_lambda_logic()
    return "200 OK"


def test_respond_with_400_when_patient_id_missing(missing_id_event, context):
    expected = ApiGatewayResponse(
        400, "An error occurred due to missing key: 'patientId'", "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(missing_id_event, context)

    assert actual == expected
    actual_lambda_logic.assert_not_called()


def test_respond_with_400_when_patient_id_invalid(invalid_id_event, context):
    expected = ApiGatewayResponse(
        400, "Invalid NHS number", "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(invalid_id_event, context)

    assert actual == expected
    actual_lambda_logic.assert_not_called()


def test_respond_with_lambda_response_when_patient_id_is_valid(valid_id_event, context):
    expected = "200 OK"

    actual = lambda_handler(valid_id_event, context)

    assert actual == expected
    actual_lambda_logic.assert_called_once()
