import json

import pytest
from botocore.exceptions import ClientError
from enums.pds_ssm_parameters import SSMParameter
from requests import Response
from services.virus_scan_result_service import VirusScanResultService
from tests.unit.helpers.data.virus_scanner.scan_results import (
    BAD_REQUEST_RESPONSE,
    CLEAN_FILE_RESPONSE,
    INFECTED_FILE_RESPONSE,
    RESPONSE_TOKEN,
)
from utils.lambda_exceptions import LambdaException, VirusScanResultException


@pytest.fixture
def virus_scanner_service(set_env, mocker):
    service = VirusScanResultService()
    mocker.patch.object(service, "ssm_service")
    yield service


def test_prepare_request_raise_error(virus_scanner_service, mocker):
    virus_scanner_service.get_ssm_parameters_for_request_access_token = (
        mocker.MagicMock()
    )
    virus_scanner_service.get_ssm_parameters_for_request_access_token.side_effect = (
        ClientError({"Error": {"Code": "500", "Message": "mocked error"}}, "test")
    )
    with pytest.raises(VirusScanResultException):
        virus_scanner_service.prepare_request("test_file_ref")


def test_virus_scan_request_successful(mocker, virus_scanner_service):
    file_ref = "test_file_ref"
    virus_scanner_service.access_token = "test_token"
    virus_scanner_service.base_url = "test.endpoint"
    excepted_headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + virus_scanner_service.access_token,
    }
    excepted_scan_url = virus_scanner_service.base_url + "/api/Scan/Existing"
    excepted_json_data_request = {
        "container": virus_scanner_service.staging_s3_bucket_name,
        "objectPath": file_ref,
    }
    response = Response()
    response.status_code = 200
    response._content = json.dumps(CLEAN_FILE_RESPONSE).encode("utf-8")
    mock_post = mocker.patch("requests.post", return_value=response)
    try:
        virus_scanner_service.virus_scan_request(
            "test_file_ref", retry_on_expired=False
        )
    except LambdaException:
        assert False, "test"

    mock_post.assert_called_with(
        url=excepted_scan_url,
        headers=excepted_headers,
        data=json.dumps(excepted_json_data_request),
    )
    mock_post.assert_called_once()


def test_virus_scan_request_invalid_token(mocker, virus_scanner_service):
    file_ref = "test_file_ref"
    virus_scanner_service.access_token = "test_token"
    virus_scanner_service.base_url = "test.endpoint"
    excepted_headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + virus_scanner_service.access_token,
    }
    excepted_scan_url = virus_scanner_service.base_url + "/api/Scan/Existing"
    excepted_json_data_request = {
        "container": virus_scanner_service.staging_s3_bucket_name,
        "objectPath": file_ref,
    }
    first_response = Response()
    first_response.status_code = 401
    second_response = Response()
    second_response.status_code = 200
    second_response._content = json.dumps(CLEAN_FILE_RESPONSE).encode("utf-8")
    mock_post = mocker.patch(
        "requests.post", side_effect=[first_response, second_response]
    )
    virus_scanner_service.get_new_access_token = mocker.MagicMock()
    try:
        virus_scanner_service.virus_scan_request("test_file_ref", retry_on_expired=True)
    except LambdaException:
        assert False, "test"

    mock_post.assert_called_with(
        url=excepted_scan_url,
        headers=excepted_headers,
        data=json.dumps(excepted_json_data_request),
    )
    virus_scanner_service.get_new_access_token.assert_called_once()
    assert mock_post.call_count == 2


def test_virus_scan_request_infected_file(mocker, virus_scanner_service):
    file_ref = "test_file_ref"
    virus_scanner_service.access_token = "test_token"
    virus_scanner_service.base_url = "test.endpoint"
    excepted_headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + virus_scanner_service.access_token,
    }
    excepted_scan_url = virus_scanner_service.base_url + "/api/Scan/Existing"
    excepted_json_data_request = {
        "container": virus_scanner_service.staging_s3_bucket_name,
        "objectPath": file_ref,
    }
    response = Response()
    response.status_code = 200
    response._content = json.dumps(INFECTED_FILE_RESPONSE).encode("utf-8")
    mock_post = mocker.patch("requests.post", return_value=response)
    with pytest.raises(VirusScanResultException):
        virus_scanner_service.virus_scan_request(
            "test_file_ref", retry_on_expired=False
        )

    mock_post.assert_called_with(
        url=excepted_scan_url,
        headers=excepted_headers,
        data=json.dumps(excepted_json_data_request),
    )
    mock_post.assert_called_once()


def test_virus_scan_request_bad_request(mocker, virus_scanner_service):
    file_ref = "test_file_ref"
    virus_scanner_service.access_token = "test_token"
    virus_scanner_service.base_url = "test.endpoint"
    excepted_headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + virus_scanner_service.access_token,
    }
    excepted_scan_url = virus_scanner_service.base_url + "/api/Scan/Existing"
    excepted_json_data_request = {
        "container": virus_scanner_service.staging_s3_bucket_name,
        "objectPath": file_ref,
    }
    response = Response()
    response.status_code = 400
    response._content = json.dumps(BAD_REQUEST_RESPONSE).encode("utf-8")
    mock_post = mocker.patch("requests.post", return_value=response)
    with pytest.raises(VirusScanResultException):
        virus_scanner_service.virus_scan_request(
            "test_file_ref", retry_on_expired=False
        )

    mock_post.assert_called_with(
        url=excepted_scan_url,
        headers=excepted_headers,
        data=json.dumps(excepted_json_data_request),
    )
    mock_post.assert_called_once()


def test_get_new_access_token_return_200(mocker, virus_scanner_service):
    response = Response()
    response.status_code = 200
    response._content = json.dumps(RESPONSE_TOKEN).encode("utf-8")
    virus_scanner_service.base_url = "test.endpoint"
    virus_scanner_service.username = "test_username"
    virus_scanner_service.password = "test_password"
    mock_post = mocker.patch("requests.post", return_value=response)

    expected = RESPONSE_TOKEN["accessToken"]
    excepted_token_url = virus_scanner_service.base_url + "/api/Token"
    excepted_json_data_request = {
        "username": virus_scanner_service.username,
        "password": virus_scanner_service.password,
    }

    virus_scanner_service.update_ssm_access_token = mocker.MagicMock()

    assert virus_scanner_service.access_token == ""
    try:
        virus_scanner_service.get_new_access_token()
    except LambdaException:
        assert False, "test"

    mock_post.assert_called_with(
        url=excepted_token_url,
        headers={"Content-type": "application/json"},
        data=json.dumps(excepted_json_data_request),
    )
    assert virus_scanner_service.access_token == expected
    virus_scanner_service.update_ssm_access_token.assert_called_once()


def test_get_new_access_token_return_400(mocker, virus_scanner_service):
    response = Response()
    response.status_code = 400
    virus_scanner_service.base_url = "test.endpoint"
    virus_scanner_service.username = "test_username"
    virus_scanner_service.password = "test_password"
    mock_post = mocker.patch("requests.post", return_value=response)

    excepted_token_url = virus_scanner_service.base_url + "/api/Token"
    excepted_json_data_request = {
        "username": virus_scanner_service.username,
        "password": virus_scanner_service.password,
    }

    virus_scanner_service.update_ssm_access_token = mocker.MagicMock()

    assert virus_scanner_service.access_token == ""
    with pytest.raises(VirusScanResultException):
        virus_scanner_service.get_new_access_token()

    mock_post.assert_called_with(
        url=excepted_token_url,
        headers={"Content-type": "application/json"},
        data=json.dumps(excepted_json_data_request),
    )
    assert virus_scanner_service.access_token == ""
    virus_scanner_service.update_ssm_access_token.assert_not_called()


def test_update_access_token_ssm(mocker, virus_scanner_service):
    virus_scanner_service.update_ssm_access_token("test_string")

    virus_scanner_service.ssm_service.update_ssm_parameter.assert_called_with(
        parameter_key=SSMParameter.VIRUS_API_ACCESSTOKEN.value,
        parameter_value="test_string",
        parameter_type="SecureString",
    )


def test_get_parameters_for_pds_api_request(virus_scanner_service):
    ssm_parameters_expected = {
        SSMParameter.VIRUS_API_ACCESSTOKEN.value: f"test_value_{SSMParameter.VIRUS_API_ACCESSTOKEN.value}",
        SSMParameter.VIRUS_API_USER.value: f"test_value_{SSMParameter.VIRUS_API_USER.value}",
        SSMParameter.VIRUS_API_PASSWORD.value: f"test_value_{SSMParameter.VIRUS_API_PASSWORD.value}",
        SSMParameter.VIRUS_API_BASEURL.value: f"test_value_{SSMParameter.VIRUS_API_BASEURL.value}",
    }
    assert virus_scanner_service.access_token == ""
    assert virus_scanner_service.username == ""
    assert virus_scanner_service.password == ""
    assert virus_scanner_service.base_url == ""

    virus_scanner_service.ssm_service.get_ssm_parameters.return_value = (
        ssm_parameters_expected
    )

    virus_scanner_service.get_ssm_parameters_for_request_access_token()

    assert (
        virus_scanner_service.access_token
        == ssm_parameters_expected[SSMParameter.VIRUS_API_ACCESSTOKEN.value]
    )
    assert (
        virus_scanner_service.username
        == ssm_parameters_expected[SSMParameter.VIRUS_API_USER.value]
    )
    assert (
        virus_scanner_service.password
        == ssm_parameters_expected[SSMParameter.VIRUS_API_PASSWORD.value]
    )
    assert (
        virus_scanner_service.base_url
        == ssm_parameters_expected[SSMParameter.VIRUS_API_BASEURL.value]
    )
