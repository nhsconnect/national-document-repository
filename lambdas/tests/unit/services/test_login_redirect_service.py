import pytest
from botocore.exceptions import ClientError
from oauthlib.oauth2 import InsecureTransportError
from services.login_redirect_service import LoginRedirectService
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
    service = LoginRedirectService()
    yield service


@pytest.fixture
def mock_dynamo(mocker, mock_service):
    yield mocker.patch.object(mock_service, "dynamodb_service")


@pytest.fixture
def mock_ssm(mocker, mock_service):
    mock_service.oidc_parameters = {
        "OIDC_AUTHORISE_URL": "string",
        "OIDC_CLIENT_ID": "string",
    }
    yield mocker.patch.object(mock_service, "ssm_service")


@pytest.fixture
def mock_oidc(mocker, mock_service):
    yield mocker.patch.object(
        mock_service, "configure_oidc", return_value=FakeWebAppClient()
    )


def test_prepare_redirect_response_returns_location_header_with_correct_headers(
    mocker, mock_service, mock_oidc, mock_ssm
):
    mocker.patch.object(mock_service, "save_state_in_dynamo_db")

    response = mock_service.prepare_redirect_response()

    expected = {"Location": RETURN_URL}

    assert response == expected
    mock_ssm.get_ssm_parameters.assert_called_once()


def test_prepare_redirect_response_return_500_when_boto3_client_failing(
    mocker, mock_service, mock_oidc, mock_ssm
):
    mock_save_state_in_dynamo_db = mocker.patch.object(
        mock_service, "save_state_in_dynamo_db"
    )
    mock_oidc.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "mocked error"}}, "test"
    )

    with pytest.raises(LoginRedirectException):
        mock_service.prepare_redirect_response()
    mock_save_state_in_dynamo_db.assert_not_called()
    mock_ssm.get_ssm_parameters.assert_called_once()


def test_prepare_redirect_response_return_500_when_auth_client_failing(
    mocker, mock_service, mock_oidc, mock_ssm
):
    mock_save_state_in_dynamo_db = mocker.patch.object(
        mock_service, "save_state_in_dynamo_db"
    )
    mock_oidc.side_effect = InsecureTransportError

    with pytest.raises(LoginRedirectException):
        mock_service.prepare_redirect_response()
    mock_save_state_in_dynamo_db.assert_not_called()
    mock_ssm.get_ssm_parameters.assert_called_once()


def test_save_to_dynamo(mocker, monkeypatch, mock_service, mock_dynamo):
    monkeypatch.setenv("AUTH_DYNAMODB_NAME", "test_table")
    mocker.patch("time.time", return_value=1238)
    expected_item = {"State": "test", "TimeToExist": 1838}

    mock_service.save_state_in_dynamo_db("test")

    mock_dynamo.create_item.assert_called_once()
    mock_dynamo.create_item.assert_called_with(
        item=expected_item, table_name="test_table"
    )
