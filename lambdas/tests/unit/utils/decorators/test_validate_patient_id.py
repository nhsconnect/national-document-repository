import json
from unittest.mock import MagicMock

from utils.decorators.validate_patient_id import validate_patient_id
from utils.lambda_response import ApiGatewayResponse

actual_lambda_logic = MagicMock()


@validate_patient_id
def lambda_handler(event, _context):
    actual_lambda_logic()
    return "200 OK"


def test_respond_with_400_when_patient_id_missing(missing_id_event, context):
    body = json.dumps(
        {"message": "An error occurred due to missing key", "err_code": "PN_4002"}
    )
    expected = ApiGatewayResponse(400, body, "GET").create_api_gateway_response()

    actual = lambda_handler(missing_id_event, context)

    assert actual == expected
    actual_lambda_logic.assert_not_called()


def test_respond_with_400_when_patient_id_invalid(invalid_id_event, context):
    nhs_number = invalid_id_event["queryStringParameters"]["patientId"]
    body = json.dumps(
        {"message": f"Invalid patient number {nhs_number}", "err_code": "PN_4001"}
    )
    expected = ApiGatewayResponse(400, body, "GET").create_api_gateway_response()

    actual = lambda_handler(invalid_id_event, context)

    assert actual == expected
    actual_lambda_logic.assert_not_called()


def test_respond_with_lambda_response_when_patient_id_is_valid(valid_id_event, context):
    expected = "200 OK"

    actual = lambda_handler(valid_id_event, context)

    assert actual == expected
    actual_lambda_logic.assert_called_once()
