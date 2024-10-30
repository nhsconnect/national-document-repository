import json

import pytest
from botocore.exceptions import ClientError
from enums.pds_ssm_parameters import SSMParameter
from requests import Response
from services.pds_api_service import PdsApiService
from tests.unit.helpers.data.pds.pds_patient_response import PDS_PATIENT
from tests.unit.helpers.mock_services import FakeSSMService
from utils.exceptions import PdsErrorException

ACCESS_TOKEN = "Sr5PGv19wTEHJdDr2wx2f7IGd0cw"

fake_ssm_service = FakeSSMService()
pds_service = PdsApiService(fake_ssm_service)


@pytest.fixture
def mock_get_patient_data(mocker):
    response = Response()
    response.status_code = 200
    response._content = json.dumps(PDS_PATIENT).encode("utf-8")

    mock_session = mocker.patch.object(pds_service, "session")
    mock_session.get.return_value = response

    yield mock_session


def test_get_parameters_for_pds_api_request():
    ssm_parameters_expected = f"test_value_{SSMParameter.PDS_API_ENDPOINT.value}"

    actual = pds_service.get_endpoint_for_pds_api_request()
    assert ssm_parameters_expected == actual


def test_pds_request_valid_token(mocker, mock_get_patient_data):
    time_now = 1600000000
    mocker.patch("time.time", return_value=time_now)
    mock_response_token = ACCESS_TOKEN

    nhs_number = "1111111111"
    mock_url_endpoint = "api.test/endpoint/Patient/" + nhs_number
    mock_authorization_header = {
        "Authorization": f"Bearer {mock_response_token}",
        "X-Request-ID": "123412342",
    }

    mock_get_parameters = mocker.patch(
        "services.pds_api_service.PdsApiService.get_endpoint_for_pds_api_request",
        return_value="api.test/endpoint/",
    )
    mock_new_access_token = mocker.patch(
        "services.pds_api_service.PdsApiService.create_access_token",
        return_value=ACCESS_TOKEN,
    )
    mocker.patch("uuid.uuid4", return_value="123412342")

    pds_service.pds_request(nhs_number="1111111111", retry_on_expired=True)

    mock_get_parameters.assert_called_once()
    mock_new_access_token.assert_called()
    mock_get_patient_data.get.assert_called_with(
        url=mock_url_endpoint, headers=mock_authorization_header
    )


def test_pds_request_expired_token(mocker, mock_get_patient_data):
    nhs_number = "1111111111"
    mock_url_endpoint = "api.test/endpoint/Patient/" + nhs_number
    new_mock_access_token = "mock_access_token"

    mock_authorization_header = {
        "Authorization": f"Bearer {new_mock_access_token}",
        "X-Request-ID": "123412342",
    }

    mock_get_parameters = mocker.patch(
        "services.pds_api_service.PdsApiService.get_endpoint_for_pds_api_request",
        return_value="api.test/endpoint/",
    )
    mocker.patch("time.time", return_value=1700000000.953031)
    mock_new_access_token = mocker.patch(
        "services.pds_api_service.PdsApiService.create_access_token",
        return_value=new_mock_access_token,
    )
    mocker.patch("uuid.uuid4", return_value="123412342")

    expected = mock_get_patient_data.get.return_value
    actual = pds_service.pds_request(nhs_number="1111111111", retry_on_expired=True)

    assert actual == expected
    mock_get_parameters.assert_called_once()
    mock_new_access_token.assert_called_once()
    mock_get_patient_data.get.assert_called_with(
        url=mock_url_endpoint, headers=mock_authorization_header
    )


def test_pds_request_valid_token_expired_response(mocker):
    first_response = Response()
    first_response.status_code = 401
    second_response = Response()
    second_response.status_code = 200
    second_response._content = json.dumps(PDS_PATIENT).encode("utf-8")
    nhs_number = "1111111111"
    mock_url_endpoint = "api.test/endpoint/Patient/" + nhs_number
    new_mock_access_token = "mock_access_token"

    mock_authorization_header = {
        "Authorization": f"Bearer {new_mock_access_token}",
        "X-Request-ID": "123412342",
    }

    mock_get_parameters = mocker.patch(
        "services.pds_api_service.PdsApiService.get_endpoint_for_pds_api_request",
        return_value="api.test/endpoint/",
    )
    mocker.patch("time.time", side_effect=[1600000000.953031, 1700000000.953031])
    mock_new_access_token = mocker.patch(
        "services.pds_api_service.PdsApiService.create_access_token",
        return_value=new_mock_access_token,
    )
    mocker.patch("uuid.uuid4", return_value="123412342")

    mock_session = mocker.patch.object(pds_service, "session")
    mock_session.get.side_effect = [first_response, second_response]

    actual = pds_service.pds_request(nhs_number="1111111111", retry_on_expired=True)

    assert actual == second_response
    assert mock_get_parameters.call_count == 2
    assert mock_new_access_token.call_count == 2
    mock_session.get.assert_called_with(
        url=mock_url_endpoint, headers=mock_authorization_header
    )


def test_pds_request_valid_token_expired_response_no_retry(mocker):
    response = Response()
    response.status_code = 401
    nhs_number = "1111111111"
    mock_url_endpoint = "api.test/endpoint/Patient/" + nhs_number
    mock_authorization_header = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "X-Request-ID": "123412342",
    }
    mock_get_parameters = mocker.patch(
        "services.pds_api_service.PdsApiService.get_endpoint_for_pds_api_request",
        return_value="api.test/endpoint/",
    )
    mocker.patch("time.time", return_value=1600000000.953031)
    mock_new_access_token = mocker.patch(
        "services.pds_api_service.PdsApiService.create_access_token",
        return_value=ACCESS_TOKEN,
    )
    mocker.patch("uuid.uuid4", return_value="123412342")

    mock_session = mocker.patch.object(pds_service, "session")
    mock_session.get.return_value = response

    actual = pds_service.pds_request(nhs_number="1111111111", retry_on_expired=False)

    assert actual == response
    mock_get_parameters.assert_called_once()
    mock_new_access_token.assert_called_once()
    mock_session.get.assert_called_with(
        url=mock_url_endpoint, headers=mock_authorization_header
    )


def test_pds_request_raise_pds_error_exception(mocker):
    with pytest.raises(PdsErrorException):
        mock_get_parameters = mocker.patch(
            "services.pds_api_service.PdsApiService.get_endpoint_for_pds_api_request",
            side_effect=ClientError(
                {"Error": {"Code": "500", "Message": "mocked error"}}, "test"
            ),
        )
        mock_new_access_token = mocker.patch(
            "services.pds_api_service.PdsApiService.get_new_access_token"
        )
        mock_post = mocker.patch("requests.get")

        pds_service.pds_request(nhs_number="1111111111", retry_on_expired=True)

        mock_get_parameters.assert_called_once()
        mock_new_access_token.assert_not_called()
        mock_post.assert_not_called()
