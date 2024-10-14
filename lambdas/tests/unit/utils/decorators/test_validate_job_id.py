from unittest.mock import MagicMock

from enums.lambda_error import LambdaError
from utils.decorators.validate_job_id import validate_job_id
from utils.lambda_response import ApiGatewayResponse

actual_lambda_logic = MagicMock()


@validate_job_id
def lambda_handler(event, _context):
    actual_lambda_logic()
    return "200 OK"


def test_respond_with_400_when_job_id_missing(missing_id_event, context):
    actual = lambda_handler(missing_id_event, context)

    body = LambdaError.ManifestMissingJobId.create_error_body()
    expected = ApiGatewayResponse(400, body, "GET").create_api_gateway_response()

    assert actual == expected
    actual_lambda_logic.assert_not_called()


def test_respond_with_400_when_query_string_missing(
    missing_query_string_event, context
):
    actual = lambda_handler(missing_query_string_event, context)

    body = LambdaError.DocTypeKey.create_error_body()
    expected = ApiGatewayResponse(400, body, "GET").create_api_gateway_response()

    assert actual == expected
    actual_lambda_logic.assert_not_called()


def test_respond_with_lambda_response_when_job_id_is_valid(valid_id_event, context):
    expected = "200 OK"

    actual = lambda_handler(valid_id_event, context)

    assert actual == expected
    actual_lambda_logic.assert_called_once()
