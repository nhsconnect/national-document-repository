import json

import pytest
from enums.pds_ssm_parameters import SSMParameter
from requests import Response
from services.base.nhs_oauth_service import NhsOauthService
from tests.unit.helpers.data.pds.access_token_response import RESPONSE_TOKEN
from tests.unit.helpers.mock_services import FakeSSMService
from utils.exceptions import OAuthErrorException

fake_ssm_service = FakeSSMService()
nhs_oauth_service = NhsOauthService(fake_ssm_service)


def mock_pds_token_response_issued_at(timestamp_in_sec: float) -> dict:
    response_token = {
        "access_token": "Sr5PGv19wTEHJdDr2wx2f7IGd0cw",
        "expires_in": "599",
        "token_type": "Bearer",
        "issued_at": str(int(timestamp_in_sec * 1000)),
    }

    return response_token


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
    nhs_oauth_service.request_new_access_token(mock_jwt_token, mock_endpoint)
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
    nhs_oauth_service.create_jwt_token_for_new_access_token_request(
        access_token_parameters
    )
    mock_jwt_encode.assert_called_with(
        expected_payload,
        "test_string_key_pds",
        algorithm="RS512",
        headers={"kid": "test_string_pds_kid"},
    )


def test_get_current_access_token():
    ssm_parameters_expected = f"test_value_{SSMParameter.PDS_API_ACCESS_TOKEN.value}"
    actual = nhs_oauth_service.get_current_access_token()
    assert ssm_parameters_expected == actual


def test_update_access_token_ssm(mocker):
    fake_ssm_service.update_ssm_parameter = mocker.MagicMock()

    nhs_oauth_service.update_access_token_ssm("test_string")

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
    nhs_oauth_service.get_parameters_for_new_access_token()
    fake_ssm_service.get_ssm_parameters.assert_called_with(
        parameters, with_decryption=True
    )


def test_get_new_access_token_raise_OAuthErrorException(mocker):
    with pytest.raises(OAuthErrorException):
        response = Response()
        response.status_code = 400
        mock_nhs_oauth_endpoint = "api.test/endpoint"
        mock_token = "test_token"
        mocker.patch(
            "services.base.nhs_oauth_service.NhsOauthService.get_parameters_for_new_access_token",
            return_value={
                SSMParameter.NHS_OAUTH_ENDPOINT.value: mock_nhs_oauth_endpoint
            },
        )
        mock_create_jwt = mocker.patch(
            "services.base.nhs_oauth_service.NhsOauthService.create_jwt_token_for_new_access_token_request",
            return_value=mock_token,
        )
        mock_api_call_oauth = mocker.patch(
            "services.base.nhs_oauth_service.NhsOauthService.request_new_access_token",
            return_value=response,
        )
        mock_update_ssm = mocker.patch(
            "services.base.nhs_oauth_service.NhsOauthService.update_access_token_ssm"
        )

        nhs_oauth_service.get_new_access_token()

        mock_create_jwt.assert_called_with(
            {SSMParameter.NHS_OAUTH_ENDPOINT.value: mock_nhs_oauth_endpoint}
        )
        mock_api_call_oauth.assert_called_with(mock_token, mock_nhs_oauth_endpoint)
        mock_update_ssm.assert_not_called()


def test_get_new_access_token_return_200(mocker):
    response = Response()
    response.status_code = 200
    response._content = json.dumps(RESPONSE_TOKEN).encode("utf-8")
    mock_nhs_oauth_endpoint = "api.test/endpoint"
    mock_token = "test_token"
    mocker.patch(
        "services.base.nhs_oauth_service.NhsOauthService.get_parameters_for_new_access_token",
        return_value={SSMParameter.NHS_OAUTH_ENDPOINT.value: mock_nhs_oauth_endpoint},
    )
    mock_create_jwt = mocker.patch(
        "services.base.nhs_oauth_service.NhsOauthService.create_jwt_token_for_new_access_token_request",
        return_value=mock_token,
    )
    mock_api_call_oauth = mocker.patch(
        "services.base.nhs_oauth_service.NhsOauthService.request_new_access_token",
        return_value=response,
    )
    mock_update_ssm = mocker.patch(
        "services.base.nhs_oauth_service.NhsOauthService.update_access_token_ssm"
    )
    expected = RESPONSE_TOKEN["access_token"]

    actual = nhs_oauth_service.get_new_access_token()

    mock_create_jwt.assert_called_with(
        {SSMParameter.NHS_OAUTH_ENDPOINT.value: mock_nhs_oauth_endpoint}
    )
    mock_api_call_oauth.assert_called_with(mock_token, mock_nhs_oauth_endpoint)
    mock_update_ssm.assert_called_with(json.dumps(RESPONSE_TOKEN))
    assert expected == actual


def test_pds_request_not_refresh_token_if_more_than_10_seconds_before_expiry(mocker):
    time_now = 1600000000
    mocker.patch("time.time", return_value=time_now)
    mock_response_token = mock_pds_token_response_issued_at(time_now - 599 + 11)

    mock_get_parameters = mocker.patch(
        "services.base.nhs_oauth_service.NhsOauthService.get_current_access_token",
        return_value=json.dumps(mock_response_token),
    )
    mock_new_access_token = mocker.patch(
        "services.base.nhs_oauth_service.NhsOauthService.get_new_access_token"
    )
    mocker.patch("uuid.uuid4", return_value="123412342")

    nhs_oauth_service.create_access_token()

    mock_get_parameters.assert_called_once()
    mock_new_access_token.assert_not_called()


def test_pds_request_refresh_token_9_seconds_before_expiration(
    mocker,
):
    time_now = 1600000000
    mocker.patch("time.time", return_value=time_now)
    mock_response_token = mock_pds_token_response_issued_at(time_now - 599 + 9)
    new_mock_access_token = "mock_access_token"

    mock_get_parameters = mocker.patch(
        "services.base.nhs_oauth_service.NhsOauthService.get_current_access_token",
        return_value=json.dumps(mock_response_token),
    )
    mock_new_access_token = mocker.patch(
        "services.base.nhs_oauth_service.NhsOauthService.get_new_access_token",
        return_value=new_mock_access_token,
    )
    mocker.patch("uuid.uuid4", return_value="123412342")

    nhs_oauth_service.create_access_token()

    mock_get_parameters.assert_called_once()
    mock_new_access_token.assert_called_once()


def test_pds_request_refresh_token_if_already_expired(mocker):
    time_now = 1600000000
    mocker.patch("time.time", return_value=time_now)
    mock_response_token = mock_pds_token_response_issued_at(time_now - 599)
    new_mock_access_token = "mock_access_token"

    mock_get_parameters = mocker.patch(
        "services.base.nhs_oauth_service.NhsOauthService.get_current_access_token",
        return_value=json.dumps(mock_response_token),
    )
    mock_new_access_token = mocker.patch(
        "services.base.nhs_oauth_service.NhsOauthService.get_new_access_token",
        return_value=new_mock_access_token,
    )
    mocker.patch("uuid.uuid4", return_value="123412342")

    nhs_oauth_service.create_access_token()

    mock_get_parameters.assert_called_once()
    mock_new_access_token.assert_called_once()


def test_pds_request_refresh_token_if_already_expired_11_seconds_ago(mocker):
    time_now = 1600000000
    mocker.patch("time.time", return_value=time_now)
    mock_response_token = mock_pds_token_response_issued_at(time_now - 599 - 11)
    new_mock_access_token = "mock_access_token"

    mock_get_parameters = mocker.patch(
        "services.base.nhs_oauth_service.NhsOauthService.get_current_access_token",
        return_value=json.dumps(mock_response_token),
    )
    mock_new_access_token = mocker.patch(
        "services.base.nhs_oauth_service.NhsOauthService.get_new_access_token",
        return_value=new_mock_access_token,
    )
    mocker.patch("uuid.uuid4", return_value="123412342")

    nhs_oauth_service.create_access_token()

    mock_get_parameters.assert_called_once()
    mock_new_access_token.assert_called_once()


def test_pds_request_expired_token(mocker):
    new_mock_access_token = "mock_access_token"

    mock_get_parameters = mocker.patch(
        "services.base.nhs_oauth_service.NhsOauthService.get_current_access_token",
        return_value=json.dumps(RESPONSE_TOKEN),
    )
    mocker.patch("time.time", return_value=1700000000.953031)
    mock_new_access_token = mocker.patch(
        "services.base.nhs_oauth_service.NhsOauthService.get_new_access_token",
        return_value=new_mock_access_token,
    )
    mocker.patch("uuid.uuid4", return_value="123412342")

    actual = nhs_oauth_service.create_access_token()
    assert actual == new_mock_access_token
    mock_get_parameters.assert_called_once()
    mock_new_access_token.assert_called_once()
