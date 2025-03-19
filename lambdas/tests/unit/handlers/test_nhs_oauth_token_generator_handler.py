import json
import time

import pytest
from handlers.nhs_oauth_token_generator_handler import lambda_handler
from utils.exceptions import OAuthErrorException

mock_token = "test_access_token"


@pytest.fixture
def mock_auth_service(mocker):
    mock = mocker.Mock()
    mocker.patch(
        "handlers.nhs_oauth_token_generator_handler.NhsOauthService", return_value=mock
    )
    return mock


@pytest.fixture
def mock_sleep(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda _: None)


def test_lambda_handler_success_on_first_attempt(mock_auth_service, event, context):
    mock_auth_service.get_nhs_oauth_response.return_value = mock_token

    lambda_handler(event, context)

    mock_auth_service.get_nhs_oauth_response.assert_called_once()
    mock_auth_service.update_access_token_ssm.assert_called_once_with(
        json.dumps(mock_token)
    )


def test_lambda_handler_success_on_retry(mock_auth_service, mock_sleep, event, context):
    mock_auth_service.get_nhs_oauth_response.side_effect = [
        OAuthErrorException("Error creating OAuth access token"),
        mock_token,
    ]

    lambda_handler(event, context)

    assert mock_auth_service.get_nhs_oauth_response.call_count == 2
    mock_auth_service.update_access_token_ssm.assert_called_once_with(
        json.dumps(mock_token)
    )


def test_lambda_handler_fails_after_max_retries(
    mock_auth_service, mock_sleep, event, context
):
    mock_auth_service.get_nhs_oauth_response.side_effect = OAuthErrorException(
        "Error creating OAuth access token"
    )

    with pytest.raises(OAuthErrorException):
        lambda_handler(event, context)

    assert mock_auth_service.get_nhs_oauth_response.call_count == 5
    mock_auth_service.update_access_token_ssm.assert_not_called()
