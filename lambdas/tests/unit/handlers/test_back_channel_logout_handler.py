import pytest
from handlers.back_channel_logout_handler import lambda_handler
from utils.exceptions import LogoutFailureException
from utils.lambda_response import ApiGatewayResponse

error_string = (
    """{"error": "failed logout", "error_description":"""
    + """ "An error occurred due to missing request body/logout token"}"""
)


@pytest.fixture
def mock_configuration_service(mocker):
    mock_service = mocker.patch(
        "handlers.back_channel_logout_handler.DynamicConfigurationService"
    )
    yield mock_service


@pytest.fixture
def mock_service(set_env, mocker):
    mocked_class = mocker.patch(
        "handlers.back_channel_logout_handler.BackChannelLogoutService"
    )
    mocked_service = mocked_class.return_value
    yield mocked_service


def test_return_400_when_missing_event(
    mock_service, event, context, mock_configuration_service
):
    expected = ApiGatewayResponse(
        400,
        error_string,
        "POST",
    ).create_api_gateway_response()

    actual = lambda_handler(event, context)
    assert expected == actual


def test_return_400_when_empty_token(mock_service, context, mock_configuration_service):
    expected = ApiGatewayResponse(
        400,
        error_string,
        "POST",
    ).create_api_gateway_response()

    actual = lambda_handler(build_event_from_token(""), context)
    assert expected == actual


def test_return_400_when_missing_token_with_string_in_body(
    mock_service, context, mock_configuration_service
):
    expected = ApiGatewayResponse(
        400,
        error_string,
        "POST",
    ).create_api_gateway_response()
    event = {"httpMethod": "POST", "body": "some_text"}

    actual = lambda_handler(event, context)
    assert expected == actual


def test_return_400_when_missing_token_with_another_body(
    mock_service, context, mock_configuration_service
):
    expected = ApiGatewayResponse(
        400,
        """{"error": "failed logout", "error_description": "An error occurred due to missing logout token"}""",
        "POST",
    ).create_api_gateway_response()
    event = {"httpMethod": "POST", "body": "some_text=something"}

    actual = lambda_handler(event, context)
    assert expected == actual


def test_return_400_when_service_raise_error(
    mock_service, context, mock_configuration_service
):
    mock_service.logout_handler.side_effect = LogoutFailureException("some_text")

    expected = ApiGatewayResponse(
        400, """{"error": "failed logout", "error_description": "some_text"}""", "POST"
    ).create_api_gateway_response()

    actual = lambda_handler(build_event_from_token("invalid_token"), context)
    assert expected == actual


def test_return_200_when_no_error_was_raised(
    mock_service, context, mock_configuration_service
):
    expected = ApiGatewayResponse(200, "", "POST").create_api_gateway_response()

    actual = lambda_handler(build_event_from_token("valid_token"), context)
    assert expected == actual


def build_event_from_token(token: str) -> dict:
    body_string = f"logout_token={token}"
    return {"httpMethod": "POST", "body": body_string}
