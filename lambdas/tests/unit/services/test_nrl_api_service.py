import pytest
from requests import Response
from services.nrl_api_service import NrlApiService
from tests.unit.helpers.mock_services import FakeSSMService, FakOAuthService
from utils.exceptions import NrlApiException

ACCESS_TOKEN = "Sr5PGv19wTEHJdDr2wx2f7IGd0cw"


@pytest.fixture
def nrl_service(set_env, mocker):

    fake_ssm_service = FakeSSMService()
    fake_auth_service = FakOAuthService(fake_ssm_service)

    nrl_service = NrlApiService(fake_ssm_service, fake_auth_service)
    mocker.patch.object(nrl_service, "session")
    yield nrl_service


def test_create_new_pointer(nrl_service):
    mock_body = {"test": "tests"}

    nrl_service.create_new_pointer(mock_body)

    nrl_service.session.post.assert_called_once()


def test_create_new_pointer_raise_error(nrl_service):
    mock_body = {"test": "tests"}
    response = Response()
    response.status_code = 400
    nrl_service.session.post.return_value = response
    pytest.raises(NrlApiException, nrl_service.create_new_pointer, mock_body)

    nrl_service.session.post.assert_called_once()


def test_get_end_user_ods_code(nrl_service):
    actual = nrl_service._get_end_user_ods_code()
    assert actual == "test_value_test_nrl_user_ods_ssm_key"
