from unittest.mock import MagicMock

from utils.decorators.override_error_check import override_error_check
from utils.lambda_response import ApiGatewayResponse

actual_lambda_logic = MagicMock()


@override_error_check
def lambda_handler(event, _context):
    actual_lambda_logic()
    return "200 OK"


def test_respond_with_400_when_error_trigger_is_400(
    valid_id_event, context, error_override_env_vars
):
    expected = ApiGatewayResponse(400, "", "GET").create_api_gateway_response()

    actual = lambda_handler(valid_id_event, context)

    assert actual == expected
    actual_lambda_logic.assert_not_called()
