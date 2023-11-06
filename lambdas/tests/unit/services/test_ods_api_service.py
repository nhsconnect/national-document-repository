import json

import pytest
from requests import Response
from services.ods_api_service import OdsApiService, parse_ods_response
from tests.unit.helpers.data.ods.utils import load_ods_response_data
from tests.unit.helpers.mock_response import MockResponse
from utils.exceptions import OdsErrorException, OrganisationNotFoundException


def test_fetch_organisation_data_returns_organisation_data(mocker):
    test_ods_code = "X26"
    ord_api_request_call_url = f"https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/{test_ods_code}"
    expected = {"successfulJSONResponse": "str"}
    response = Response()
    response.status_code = 200
    response._content = json.dumps(expected).encode("utf-8")

    mock_api = mocker.patch("requests.get", return_value=response)

    actual = OdsApiService.fetch_organisation_data(OdsApiService(), test_ods_code)

    assert actual == expected
    mock_api.assert_called_with(ord_api_request_call_url)


def test_fetch_organisation_data_404_raise_OrganisationNotFoundException(mocker):
    response_404 = MockResponse(404, {"errorCode": 404, "errorText": "Not found"})

    mocker.patch("requests.get", return_value=response_404)
    with pytest.raises(OrganisationNotFoundException):
        OdsApiService.fetch_organisation_data(OdsApiService(), "non-existent-ods-code")


def test_fetch_organisation_data_catch_all_raises_OdsErrorException(mocker):
    response_400 = MockResponse(400, "BadRequest")

    mocker.patch("requests.get", return_value=response_400)

    with pytest.raises(OdsErrorException):
        OdsApiService.fetch_organisation_data(OdsApiService(), "bad-ods-code")


@pytest.fixture()
def mock_ods_responses():
    # load test data from several json files and pass to below tests in a dict
    yield load_ods_response_data()


def test_parse_ods_response_extracts_data_and_includes_role_code_passed_as_arg(
    mock_ods_responses,
):
    test_response = mock_ods_responses["pcse_org"]
    role_code = "this should be the role code and not the one in the mock data"

    actual = parse_ods_response(test_response, role_code)
    expected = {
        "name": "Primary Care Support England",
        "org_ods_code": "B9A5A",
        "role_code": role_code,
    }

    assert actual == expected


# TODO: fetch_organisation_with_permitted_role, find_and_get_gpp_org_code, find_and_get_pcse_ods
