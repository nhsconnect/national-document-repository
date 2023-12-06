import pytest
from botocore.exceptions import ClientError
from oauthlib.oauth2 import InsecureTransportError
from services.login_redirect_service import LoginRedirectService
from tests.unit.helpers.mock_services import FakeSSMService
from tests.unit.helpers.ssm_responses import \
    MOCK_MULTI_STRING_PARAMETERS_RESPONSE
from utils.exceptions import LoginRedirectException

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

    @staticmethod
    def prepare_authorization_request(*args, **kwargs):
        return RETURN_URL, "", ""


@pytest.fixture
def mock_service(mocker, set_env):
    mocker.patch("boto3.resource")
    mocker.patch("boto3.client")
    mock_ssm = mocker.patch.object("service", "ssm_service")
    mock_ssm.get_ssm_parameters.return_value = MOCK_MULTI_STRING_PARAMETERS_RESPONSE
    service = LoginRedirectService()
    mock_ssm = mocker.patch.object(service, "ssm_service")
    mock_ssm.get_ssm_parameters.return_value = MOCK_MULTI_STRING_PARAMETERS_RESPONSE
    mocker.patch.object(service, "oidc_client", return_value=FakeWebAppClient)
    mocker.patch.object(service, "dynamodb_service")
    yield service


def test_prepare_redirect_response_returns_location_header_with_correct_headers(
    mocker, set_env, mock_service
):
    mocker.patch.object(mock_service, "save_state_in_dynamo_db")

    response = mock_service.prepare_redirect_response()

    expected = {"Location": RETURN_URL}

    assert response == expected


def test_prepare_redirect_response_return_500_when_boto3_client_failing(
    mocker, set_env, login_redirect_service, mock_dynamodb_service
):
    mock_save_state_in_dynamo_db = mocker.patch.object(
        login_redirect_service, "save_state_in_dynamo_db"
    )
    mocker.patch.object(
        FakeSSMService,
        "get_ssm_parameters",
        side_effect=ClientError(
            {"Error": {"Code": "500", "Message": "mocked error"}}, "test"
        ),
    )

    with pytest.raises(LoginRedirectException):
        login_redirect_service.prepare_redirect_response(
            FakeWebAppClient, FakeSSMService, mock_dynamodb_service
        )
    mock_save_state_in_dynamo_db.assert_not_called()


def test_prepare_redirect_response_return_500_when_auth_client_failing(
    mocker, set_env, login_redirect_service
):
    mock_save_state_in_dynamo_db = mocker.patch.object(
        login_redirect_service, "save_state_in_dynamo_db"
    )
    mocker.patch.object(
        FakeSSMService, "get_ssm_parameters", side_effect=InsecureTransportError
    )

    with pytest.raises(LoginRedirectException):
        login_redirect_service.prepare_redirect_response()
    mock_save_state_in_dynamo_db.assert_not_called()


def test_save_to_dynamo(
    mocker, monkeypatch, login_redirect_service, mock_dynamodb_service
):
    monkeypatch.setenv("AUTH_DYNAMODB_NAME", "test_table")
    mocker.patch("time.time", return_value=1238)
    expected_item = {"State": "test", "TimeToExist": 1838}

    login_redirect_service.save_state_in_dynamo_db("test")

    mock_dynamodb_service.create_item.assert_called_once()
    mock_dynamodb_service.create_item.assert_called_with(
        item=expected_item, table_name="test_table"
    )
