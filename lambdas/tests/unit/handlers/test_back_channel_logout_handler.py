from handlers.back_channel_logout_handler import (back_channel_logout_service,
                                                  lambda_handler)
from utils.exceptions import LogoutFailureException
from utils.lambda_response import ApiGatewayResponse

error_string = (
    """{"error": "failed logout", "error_description":"""
    + """ "An error occurred due to missing request body/logout token"}"""
)


def test_return_400_when_missing_event(set_env, event, context):
    expected = ApiGatewayResponse(
        400,
        error_string,
        "POST",
    ).create_api_gateway_response()

    actual = lambda_handler(event, context)
    assert expected == actual


def test_return_400_when_empty_token(set_env, context):
    expected = ApiGatewayResponse(
        400,
        error_string,
        "POST",
    ).create_api_gateway_response()

    actual = lambda_handler(build_event_from_token(""), context)
    assert expected == actual


def test_return_400_when_missing_token_with_string_in_body(set_env, context):
    expected = ApiGatewayResponse(
        400,
        error_string,
        "POST",
    ).create_api_gateway_response()
    event = {"httpMethod": "POST", "body": "some_text"}

    actual = lambda_handler(event, context)
    assert expected == actual


def test_return_400_when_missing_token_with_another_body(set_env, context):
    expected = ApiGatewayResponse(
        400,
        """{"error": "failed logout", "error_description": "An error occurred due to missing logout token"}""",
        "POST",
    ).create_api_gateway_response()
    event = {"httpMethod": "POST", "body": "some_text=something"}

    actual = lambda_handler(event, context)
    assert expected == actual


def test_return_400_when_service_raise_error(mocker, set_env, context):
    mocker.patch.object(
        back_channel_logout_service,
        "logout_handler",
        side_effect=LogoutFailureException("some_text"),
    )
    expected = ApiGatewayResponse(
        400, """{"error": "failed logout", "error_description": "some_text"}""", "POST"
    ).create_api_gateway_response()

    actual = lambda_handler(build_event_from_token("invalid_token"), context)
    assert expected == actual


def test_return_200_when_no_error_was_raised(mocker, set_env, context):
    mocker.patch.object(back_channel_logout_service, "logout_handler")
    expected = ApiGatewayResponse(200, "", "POST").create_api_gateway_response()

    actual = lambda_handler(build_event_from_token("valid_token"), context)
    assert expected == actual


def build_event_from_token(token: str) -> dict:
    body_string = f"logout_token={token}"
    return {"httpMethod": "POST", "body": body_string}
