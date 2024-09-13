import json

import pytest
from botocore.exceptions import ClientError
from enums.pds_ssm_parameters import SSMParameter
from requests import Response
from services.pds_api_service import PdsApiService
from tests.unit.helpers.data.pds.access_token_response import RESPONSE_TOKEN
from tests.unit.helpers.data.pds.pds_patient_response import PDS_PATIENT
from utils.exceptions import PdsErrorException


class FakeSSMService:
    def __init__(self, *arg, **kwargs):
        pass

    def get_ssm_parameters(self, parameters_keys, *arg, **kwargs):
        return {parameter: f"test_value_{parameter}" for parameter in parameters_keys}

    def update_ssm_parameter(self, *arg, **kwargs):
        pass


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


def test_request_new_token_is_call_with_correct_data(mocker):
    mock_jwt_token = "testtest"
    mock_endpoint = "api.endpoint/mock"
    access_token_headers = {"content-type": "application/x-www-form-urlencoded"}
    access_token_data = {
        "grant_type": "client_credentials",
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": mock_jwt_token,
    }
    mock_post = mocker.patch("requests.post")
    pds_service.request_new_access_token(mock_jwt_token, mock_endpoint)
    mock_post.assert_called_with(
        url=mock_endpoint, headers=access_token_headers, data=access_token_data
    )


def test_create_jwt_for_new_access_token(mocker):
    access_token_parameters = {
        SSMParameter.NHS_OAUTH_ENDPOINT.value: "api.endpoint/mock",
        SSMParameter.PDS_KID.value: "test_string_pds_kid",
        SSMParameter.NHS_OAUTH_KEY.value: "test_string_key_oauth",
        SSMParameter.PDS_API_KEY.value: "test_string_key_pds",
    }
    expected_payload = {
        "iss": "test_string_key_oauth",
        "sub": "test_string_key_oauth",
        "aud": "api.endpoint/mock",
        "jti": "123412342",
        "exp": 1534,
    }
    mocker.patch("time.time", return_value=1234.1)
    mocker.patch("uuid.uuid4", return_value="123412342")

    mock_jwt_encode = mocker.patch("jwt.encode")
    pds_service.create_jwt_token_for_new_access_token_request(access_token_parameters)
    mock_jwt_encode.assert_called_with(
        expected_payload,
        "test_string_key_pds",
        algorithm="RS512",
        headers={"kid": "test_string_pds_kid"},
    )


def test_get_parameters_for_pds_api_request():
    ssm_parameters_expected = (
        f"test_value_{SSMParameter.PDS_API_ENDPOINT.value}",
        f"test_value_{SSMParameter.PDS_API_ACCESS_TOKEN.value}",
    )
    actual = pds_service.get_parameters_for_pds_api_request()
    assert ssm_parameters_expected == actual


def test_update_access_token_ssm(mocker):
    fake_ssm_service.update_ssm_parameter = mocker.MagicMock()

    pds_service.update_access_token_ssm("test_string")

    fake_ssm_service.update_ssm_parameter.assert_called_with(
        parameter_key=SSMParameter.PDS_API_ACCESS_TOKEN.value,
        parameter_value="test_string",
        parameter_type="SecureString",
    )


def test_get_parameters_for_new_access_token(mocker):
    parameters = [
        SSMParameter.NHS_OAUTH_ENDPOINT.value,
        SSMParameter.PDS_KID.value,
        SSMParameter.NHS_OAUTH_KEY.value,
        SSMParameter.PDS_API_KEY.value,
    ]
    fake_ssm_service.get_ssm_parameters = mocker.MagicMock()
    pds_service.get_parameters_for_new_access_token()
    fake_ssm_service.get_ssm_parameters.assert_called_with(
        parameters, with_decryption=True
    )


def test_get_new_access_token_return_200(mocker):
    response = Response()
    response.status_code = 200
    response._content = json.dumps(RESPONSE_TOKEN).encode("utf-8")
    mock_nhs_oauth_endpoint = "api.test/endpoint"
    mock_token = "test_token"
    mocker.patch(
        "services.pds_api_service.PdsApiService.get_parameters_for_new_access_token",
        return_value={SSMParameter.NHS_OAUTH_ENDPOINT.value: mock_nhs_oauth_endpoint},
    )
    mock_create_jwt = mocker.patch(
        "services.pds_api_service.PdsApiService.create_jwt_token_for_new_access_token_request",
        return_value=mock_token,
    )
    mock_api_call_oauth = mocker.patch(
        "services.pds_api_service.PdsApiService.request_new_access_token",
        return_value=response,
    )
    mock_update_ssm = mocker.patch(
        "services.pds_api_service.PdsApiService.update_access_token_ssm"
    )
    expected = RESPONSE_TOKEN["access_token"]

    actual = pds_service.get_new_access_token()

    mock_create_jwt.assert_called_with(
        {SSMParameter.NHS_OAUTH_ENDPOINT.value: mock_nhs_oauth_endpoint}
    )
    mock_api_call_oauth.assert_called_with(mock_token, mock_nhs_oauth_endpoint)
    mock_update_ssm.assert_called_with(json.dumps(RESPONSE_TOKEN))
    assert expected == actual


def test_get_new_access_token_raise_PdsErrorException(mocker):
    with pytest.raises(PdsErrorException):
        response = Response()
        response.status_code = 400
        mock_nhs_oauth_endpoint = "api.test/endpoint"
        mock_token = "test_token"
        mocker.patch(
            "services.pds_api_service.PdsApiService.get_parameters_for_new_access_token",
            return_value={
                SSMParameter.NHS_OAUTH_ENDPOINT.value: mock_nhs_oauth_endpoint
            },
        )
        mock_create_jwt = mocker.patch(
            "services.pds_api_service.PdsApiService.create_jwt_token_for_new_access_token_request",
            return_value=mock_token,
        )
        mock_api_call_oauth = mocker.patch(
            "services.pds_api_service.PdsApiService.request_new_access_token",
            return_value=response,
        )
        mock_update_ssm = mocker.patch(
            "services.pds_api_service.PdsApiService.update_access_token_ssm"
        )

        pds_service.get_new_access_token()

        mock_create_jwt.assert_called_with(
            {SSMParameter.NHS_OAUTH_ENDPOINT.value: mock_nhs_oauth_endpoint}
        )
        mock_api_call_oauth.assert_called_with(mock_token, mock_nhs_oauth_endpoint)
        mock_update_ssm.assert_not_called()


def mock_pds_token_response_issued_at(timestamp_in_sec: float) -> dict:
    response_token = {
        "access_token": "Sr5PGv19wTEHJdDr2wx2f7IGd0cw",
        "expires_in": "599",
        "token_type": "Bearer",
        "issued_at": str(int(timestamp_in_sec * 1000)),
    }

    return response_token


def test_pds_request_valid_token(mocker, mock_get_patient_data):
    time_now = 1600000000
    mocker.patch("time.time", return_value=time_now)
    mock_response_token = mock_pds_token_response_issued_at(time_now)

    mock_api_request_parameters = (
        "api.test/endpoint/",
        json.dumps(mock_response_token),
    )
    nhs_number = "1111111111"
    mock_url_endpoint = "api.test/endpoint/Patient/" + nhs_number
    mock_authorization_header = {
        "Authorization": f"Bearer {mock_response_token['access_token']}",
        "X-Request-ID": "123412342",
    }

    mock_get_parameters = mocker.patch(
        "services.pds_api_service.PdsApiService.get_parameters_for_pds_api_request",
        return_value=mock_api_request_parameters,
    )
    mock_new_access_token = mocker.patch(
        "services.pds_api_service.PdsApiService.get_new_access_token"
    )
    mocker.patch("uuid.uuid4", return_value="123412342")

    pds_service.pds_request(nhs_number="1111111111", retry_on_expired=True)

    mock_get_parameters.assert_called_once()
    mock_new_access_token.assert_not_called()
    mock_get_patient_data.get.assert_called_with(
        url=mock_url_endpoint, headers=mock_authorization_header
    )


def test_pds_request_not_refresh_token_if_more_than_10_seconds_before_expiry(
    mocker, mock_get_patient_data
):
    time_now = 1600000000
    mocker.patch("time.time", return_value=time_now)
    mock_response_token = mock_pds_token_response_issued_at(time_now - 599 + 11)

    mock_api_request_parameters = (
        "api.test/endpoint/",
        json.dumps(mock_response_token),
    )

    mock_get_parameters = mocker.patch(
        "services.pds_api_service.PdsApiService.get_parameters_for_pds_api_request",
        return_value=mock_api_request_parameters,
    )
    mock_new_access_token = mocker.patch(
        "services.pds_api_service.PdsApiService.get_new_access_token"
    )
    mocker.patch("uuid.uuid4", return_value="123412342")

    pds_service.pds_request(nhs_number="1111111111", retry_on_expired=True)

    mock_get_parameters.assert_called_once()
    mock_new_access_token.assert_not_called()


def test_pds_request_refresh_token_9_seconds_before_expiration(
    mocker, mock_get_patient_data
):
    time_now = 1600000000
    mocker.patch("time.time", return_value=time_now)
    mock_response_token = mock_pds_token_response_issued_at(time_now - 599 + 9)
    new_mock_access_token = "mock_access_token"

    mock_api_request_parameters = (
        "api.test/endpoint/",
        json.dumps(mock_response_token),
    )
    nhs_number = "1111111111"
    mock_url_endpoint = "api.test/endpoint/Patient/" + nhs_number
    mock_authorization_header = {
        "Authorization": f"Bearer {new_mock_access_token}",
        "X-Request-ID": "123412342",
    }

    mock_get_parameters = mocker.patch(
        "services.pds_api_service.PdsApiService.get_parameters_for_pds_api_request",
        return_value=mock_api_request_parameters,
    )
    mock_new_access_token = mocker.patch(
        "services.pds_api_service.PdsApiService.get_new_access_token",
        return_value=new_mock_access_token,
    )
    mocker.patch("uuid.uuid4", return_value="123412342")

    pds_service.pds_request(nhs_number="1111111111", retry_on_expired=True)

    mock_get_parameters.assert_called_once()
    mock_new_access_token.assert_called_once()
    mock_get_patient_data.get.assert_called_with(
        url=mock_url_endpoint, headers=mock_authorization_header
    )


def test_pds_request_refresh_token_if_already_expired(mocker, mock_get_patient_data):
    time_now = 1600000000
    mocker.patch("time.time", return_value=time_now)
    mock_response_token = mock_pds_token_response_issued_at(time_now - 599)
    new_mock_access_token = "mock_access_token"

    mock_api_request_parameters = (
        "api.test/endpoint/",
        json.dumps(mock_response_token),
    )
    nhs_number = "1111111111"
    mock_url_endpoint = "api.test/endpoint/Patient/" + nhs_number
    mock_authorization_header = {
        "Authorization": f"Bearer {new_mock_access_token}",
        "X-Request-ID": "123412342",
    }

    mock_get_parameters = mocker.patch(
        "services.pds_api_service.PdsApiService.get_parameters_for_pds_api_request",
        return_value=mock_api_request_parameters,
    )
    mock_new_access_token = mocker.patch(
        "services.pds_api_service.PdsApiService.get_new_access_token",
        return_value=new_mock_access_token,
    )
    mocker.patch("uuid.uuid4", return_value="123412342")

    pds_service.pds_request(nhs_number="1111111111", retry_on_expired=True)

    mock_get_parameters.assert_called_once()
    mock_new_access_token.assert_called_once()
    mock_get_patient_data.get.assert_called_with(
        url=mock_url_endpoint, headers=mock_authorization_header
    )


def test_pds_request_refresh_token_if_already_expired_11_seconds_ago(
    mocker, mock_get_patient_data
):
    time_now = 1600000000
    mocker.patch("time.time", return_value=time_now)
    mock_response_token = mock_pds_token_response_issued_at(time_now - 599 - 11)
    new_mock_access_token = "mock_access_token"

    mock_api_request_parameters = (
        "api.test/endpoint/",
        json.dumps(mock_response_token),
    )
    nhs_number = "1111111111"
    mock_url_endpoint = "api.test/endpoint/Patient/" + nhs_number
    mock_authorization_header = {
        "Authorization": f"Bearer {new_mock_access_token}",
        "X-Request-ID": "123412342",
    }

    mock_get_parameters = mocker.patch(
        "services.pds_api_service.PdsApiService.get_parameters_for_pds_api_request",
        return_value=mock_api_request_parameters,
    )
    mock_new_access_token = mocker.patch(
        "services.pds_api_service.PdsApiService.get_new_access_token",
        return_value=new_mock_access_token,
    )
    mocker.patch("uuid.uuid4", return_value="123412342")

    pds_service.pds_request(nhs_number="1111111111", retry_on_expired=True)

    mock_get_parameters.assert_called_once()
    mock_new_access_token.assert_called_once()
    mock_get_patient_data.get.assert_called_with(
        url=mock_url_endpoint, headers=mock_authorization_header
    )


def test_pds_request_expired_token(mocker, mock_get_patient_data):
    response = Response()
    response.status_code = 200
    response._content = json.dumps(PDS_PATIENT).encode("utf-8")
    mock_api_request_parameters = ("api.test/endpoint/", json.dumps(RESPONSE_TOKEN))
    nhs_number = "1111111111"
    mock_url_endpoint = "api.test/endpoint/Patient/" + nhs_number
    new_mock_access_token = "mock_access_token"

    mock_authorization_header = {
        "Authorization": f"Bearer {new_mock_access_token}",
        "X-Request-ID": "123412342",
    }

    mock_get_parameters = mocker.patch(
        "services.pds_api_service.PdsApiService.get_parameters_for_pds_api_request",
        return_value=mock_api_request_parameters,
    )
    mocker.patch("time.time", return_value=1700000000.953031)
    mock_new_access_token = mocker.patch(
        "services.pds_api_service.PdsApiService.get_new_access_token",
        return_value=new_mock_access_token,
    )
    mocker.patch("uuid.uuid4", return_value="123412342")
    mocker.patch("requests.get", return_value=response)

    actual = pds_service.pds_request(nhs_number="1111111111", retry_on_expired=True)

    assert actual == response
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
    mock_api_request_parameters = ("api.test/endpoint/", json.dumps(RESPONSE_TOKEN))
    nhs_number = "1111111111"
    mock_url_endpoint = "api.test/endpoint/Patient/" + nhs_number
    new_mock_access_token = "mock_access_token"

    mock_authorization_header = {
        "Authorization": f"Bearer {new_mock_access_token}",
        "X-Request-ID": "123412342",
    }

    mock_get_parameters = mocker.patch(
        "services.pds_api_service.PdsApiService.get_parameters_for_pds_api_request",
        return_value=mock_api_request_parameters,
    )
    mocker.patch("time.time", side_effect=[1600000000.953031, 1700000000.953031])
    mock_new_access_token = mocker.patch(
        "services.pds_api_service.PdsApiService.get_new_access_token",
        return_value=new_mock_access_token,
    )
    mocker.patch("uuid.uuid4", return_value="123412342")

    mock_session = mocker.patch.object(pds_service, "session")
    mock_session.get.side_effect = [first_response, second_response]

    actual = pds_service.pds_request(nhs_number="1111111111", retry_on_expired=True)

    assert actual == second_response
    assert mock_get_parameters.call_count == 2
    mock_new_access_token.assert_called_once()

    mock_session.get.assert_called_with(
        url=mock_url_endpoint, headers=mock_authorization_header
    )


def test_pds_request_valid_token_expired_response_no_retry(mocker):
    response = Response()
    response.status_code = 401
    mock_api_request_parameters = ("api.test/endpoint/", json.dumps(RESPONSE_TOKEN))
    nhs_number = "1111111111"
    mock_url_endpoint = "api.test/endpoint/Patient/" + nhs_number
    mock_authorization_header = {
        "Authorization": f"Bearer {RESPONSE_TOKEN['access_token']}",
        "X-Request-ID": "123412342",
    }
    mock_get_parameters = mocker.patch(
        "services.pds_api_service.PdsApiService.get_parameters_for_pds_api_request",
        return_value=mock_api_request_parameters,
    )
    mocker.patch("time.time", return_value=1600000000.953031)
    mock_new_access_token = mocker.patch(
        "services.pds_api_service.PdsApiService.get_new_access_token"
    )
    mocker.patch("uuid.uuid4", return_value="123412342")

    mock_session = mocker.patch.object(pds_service, "session")
    mock_session.get.return_value = response

    actual = pds_service.pds_request(nhs_number="1111111111", retry_on_expired=False)

    assert actual == response
    mock_get_parameters.assert_called_once()
    mock_new_access_token.assert_not_called()
    mock_session.get.assert_called_with(
        url=mock_url_endpoint, headers=mock_authorization_header
    )


def test_pds_request_raise_pds_error_exception(mocker):
    with pytest.raises(PdsErrorException):
        mock_get_parameters = mocker.patch(
            "services.pds_api_service.PdsApiService.get_parameters_for_pds_api_request",
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
