import pytest
from requests import Response
from services.nrl_api_service import NrlApiService
from tests.unit.conftest import FAKE_URL, TEST_NHS_NUMBER
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
    actual = nrl_service.get_end_user_ods_code()
    assert actual == "test_value_test_nrl_user_ods_ssm_key"


def test_get_pointer_with_record_type(mocker, nrl_service):
    mock_type = 11111111
    mocker.patch("uuid.uuid4", return_value="test_uuid")

    mock_params = {
        "subject:identifier": f"https://fhir.nhs.uk/Id/nhs-number|{TEST_NHS_NUMBER}",
        "type": f"http://snomed.info/sct|{mock_type}",
    }
    mock_headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "NHSD-End-User-Organisation-ODS": "test_value_test_nrl_user_ods_ssm_key",
        "Accept": "application/json",
        "X-Request-ID": "test_uuid",
    }
    nrl_service.get_pointer(TEST_NHS_NUMBER, mock_type)

    nrl_service.session.get.assert_called_with(
        params=mock_params, url=FAKE_URL, headers=mock_headers
    )


def test_get_pointer_with_record_type_no_retry(mocker, nrl_service):
    mock_type = 11111111
    mocker.patch("uuid.uuid4", return_value="test_uuid")
    mock_params = {
        "subject:identifier": f"https://fhir.nhs.uk/Id/nhs-number|{TEST_NHS_NUMBER}",
        "type": f"http://snomed.info/sct|{mock_type}",
    }
    mock_headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "NHSD-End-User-Organisation-ODS": "test_value_test_nrl_user_ods_ssm_key",
        "Accept": "application/json",
        "X-Request-ID": "test_uuid",
    }
    response = Response()
    response.status_code = 401
    response._content = b"{}"
    nrl_service.session.get.return_value = response
    with pytest.raises(NrlApiException):
        nrl_service.get_pointer(TEST_NHS_NUMBER, mock_type, retry_on_expired=False)

    nrl_service.session.get.assert_called_with(
        params=mock_params, url=FAKE_URL, headers=mock_headers
    )
    nrl_service.session.get.assert_called_once()


def test_get_pointer_with_record_type_with_retry(mocker, nrl_service):
    mock_type = 11111111
    mocker.patch("uuid.uuid4", return_value="test_uuid")
    mock_params = {
        "subject:identifier": f"https://fhir.nhs.uk/Id/nhs-number|{TEST_NHS_NUMBER}",
        "type": f"http://snomed.info/sct|{mock_type}",
    }
    mock_headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "NHSD-End-User-Organisation-ODS": "test_value_test_nrl_user_ods_ssm_key",
        "Accept": "application/json",
        "X-Request-ID": "test_uuid",
    }
    response = Response()
    response.status_code = 401
    response._content = b"{}"
    nrl_service.session.get.return_value = response
    with pytest.raises(NrlApiException):
        nrl_service.get_pointer(TEST_NHS_NUMBER, mock_type, retry_on_expired=True)

    nrl_service.session.get.assert_called_with(
        params=mock_params, url=FAKE_URL, headers=mock_headers
    )
    assert nrl_service.session.get.call_count == 2


def test_get_pointer_raise_error(nrl_service):
    response = Response()
    response.status_code = 400
    response._content = b"{}"

    mock_type = 11111111

    nrl_service.session.get.return_value = response
    pytest.raises(NrlApiException, nrl_service.get_pointer, TEST_NHS_NUMBER, mock_type)

    nrl_service.session.get.assert_called_once()


def test_delete_pointer_with_record_type_no_record(mocker, nrl_service):
    mock_type = 11111111
    mocker.patch("uuid.uuid4", return_value="test_uuid")

    nrl_response = {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": 0,
        "entry": [],
    }
    nrl_service.get_pointer = mocker.MagicMock(return_value=nrl_response)
    nrl_service.delete_pointer(TEST_NHS_NUMBER, mock_type)

    nrl_service.session.delete.assert_not_called()


def test_delete_pointer_with_record_type_one_record(mocker, nrl_service):
    mock_type = 11111111
    mocker.patch("uuid.uuid4", return_value="test_uuid")
    mock_pointer_id = "ODSCODE-1111bfb1-1111-2222-3333-4444555c666f"
    mock_headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "NHSD-End-User-Organisation-ODS": "test_value_test_nrl_user_ods_ssm_key",
        "Accept": "application/json",
        "X-Request-ID": "test_uuid",
    }
    nrl_response = {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": 1,
        "entry": [
            {
                "resource": {
                    "resourceType": "DocumentReference",
                    "id": mock_pointer_id,
                }
            }
        ],
    }
    nrl_service.get_pointer = mocker.MagicMock(return_value=nrl_response)
    nrl_service.delete_pointer(TEST_NHS_NUMBER, mock_type)

    nrl_service.session.delete.assert_called_with(
        url=FAKE_URL + "/" + mock_pointer_id, headers=mock_headers
    )


def test_delete_pointer_with_record_type_more_than_one_record(mocker, nrl_service):
    mock_type = 11111111
    mocker.patch("uuid.uuid4", return_value="test_uuid")
    mock_pointer_id = "ODSCODE-1111bfb1-1111-2222-3333-4444555c666"

    nrl_response = {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": 1,
        "entry": [
            {
                "resource": {
                    "resourceType": "DocumentReference",
                    "id": mock_pointer_id + "1",
                }
            },
            {
                "resource": {
                    "resourceType": "DocumentReference",
                    "id": mock_pointer_id + "2",
                }
            },
        ],
    }
    nrl_service.get_pointer = mocker.MagicMock(return_value=nrl_response)
    nrl_service.delete_pointer(TEST_NHS_NUMBER, mock_type)

    assert nrl_service.session.delete.call_count == 2


def test_delete_pointer_not_raise_error(mocker, nrl_service):
    response = Response()
    response.status_code = 400
    response._content = b"{}"
    mock_type = 11111111
    nrl_response = {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": 1,
        "entry": [
            {
                "resource": {
                    "resourceType": "DocumentReference",
                    "id": "222",
                }
            }
        ],
    }
    nrl_service.get_pointer = mocker.MagicMock(return_value=nrl_response)
    nrl_service.session.delete.return_value = response
    try:
        nrl_service.delete_pointer(TEST_NHS_NUMBER, mock_type)
    except Exception:
        assert False
    nrl_service.session.delete.assert_called_once()
