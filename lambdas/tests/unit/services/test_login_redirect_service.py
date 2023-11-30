import pytest
from botocore.exceptions import ClientError
from helpers.mock_services import FakeSSMService
from oauthlib.oauth2 import InsecureTransportError
from services.login_redirect_service import LoginRedirectService
from utils.lambda_response import ApiGatewayResponse

RETURN_URL = (
    "https://www.string_value_1.com?"
    "response_type=code&"
    "client_id=1122121212&"
    "redirect_uri=https%3A%2F%2Fwww.testexample.com%&"
    "state=test1state&"
    "scope=openid+profile+nationalrbacaccess+associatedorgs"
)


class FakeWebAppClient:
    def __init__(self, *arg, **kwargs):
        self.state = "test1state"

    def prepare_authorization_request(self, *args, **kwargs):
        return RETURN_URL, "", ""


@pytest.fixture()
def login_redirect_service(mocker):
    patched_login_redirect_service = LoginRedirectService()
    # mocker.patch.object(patched_login_redirect_service.save_state_in_dynamo_db, "dynamodb_service")
    mocker.patch(
        "services.login_redirect_service.LoginRedirectService.save_state_in_dynamo_db"
    )
    yield patched_login_redirect_service


def test_prepare_redirect_response_return_303_with_correct_headers(
    mocker, monkeypatch, login_redirect_service
):
    monkeypatch.setenv("OIDC_CALLBACK_URL", "https://www.testexample.com")
    response = login_redirect_service.prepare_redirect_response(
        FakeWebAppClient, FakeSSMService()
    )
    location_header = {"Location": RETURN_URL}

    expected = ApiGatewayResponse(303, "", "GET").create_api_gateway_response(
        headers=location_header
    )

    assert response == expected
    login_redirect_service.save_state_in_dynamo_db.assert_called_once_with("test1state")
    # FakeSSMService.get_ssm_parameters.assert_called_once()


def test_prepare_redirect_response_return_500_when_boto3_client_failing(
    mocker, monkeypatch, login_redirect_service
):
    monkeypatch.setenv("OIDC_CALLBACK_URL", "https://www.testexample.com")
    mocker.patch(
        "services.login_redirect_service.save_state_in_dynamo_db"
    )
    mock_ssm_service = mocker.patch(
        "handlers.login_redirect_handler.get_ssm_parameters",
        side_effect=ClientError(
            {"Error": {"Code": "500", "Message": "mocked error"}}, "test"
        ),
    )
    response = login_redirect_service.prepare_redirect_response(
        FakeWebAppClient, FakeSSMService
    )

    expected = ApiGatewayResponse(
        500, "Server error", "GET"
    ).create_api_gateway_response()

    assert response == expected
    login_redirect_service.save_state_in_dynamo_db.assert_not_called()
    mock_ssm_service.assert_called_once()


def test_prepare_redirect_response_return_500_when_auth_client_failing(
    mocker, monkeypatch, login_redirect_service
):
    monkeypatch.setenv("OIDC_CALLBACK_URL", "https://www.testexample.com")
    mock_dynamo_service = mocker.patch(
        "handlers.login_redirect_handler.save_state_in_dynamo_db"
    )
    mock_ssm_service = mocker.patch(
        "handlers.login_redirect_handler.get_ssm_parameters",
        side_effect=InsecureTransportError(),
    )
    response = login_redirect_service.prepare_redirect_response(
        FakeWebAppClient, FakeSSMService
    )

    expected = ApiGatewayResponse(
        500, "Server error", "GET"
    ).create_api_gateway_response()

    assert response == expected
    mock_dynamo_service.assert_not_called()
    mock_ssm_service.assert_called_once()


def test_save_to_dynamo(mocker, monkeypatch, login_redirect_service):
    monkeypatch.setenv("AUTH_DYNAMODB_NAME", "test_table")
    mock_dynamo_service = mocker.patch(
        "handlers.login_redirect_handler.DynamoDBService"
    )
    mocked_dynamo_service_instance = mocker.MagicMock()
    mock_dynamo_service.return_value = mocked_dynamo_service_instance
    mocker.patch("time.time", return_value=1238)
    expected_item = {"State": "test", "TimeToExist": 1838}

    login_redirect_service.save_state_in_dynamo_db("test")

    mock_dynamo_service.assert_called_once()
    mocked_dynamo_service_instance.create_item.assert_called_once()
    mocked_dynamo_service_instance.create_item.assert_called_with(
        item=expected_item, table_name="test_table"
    )
