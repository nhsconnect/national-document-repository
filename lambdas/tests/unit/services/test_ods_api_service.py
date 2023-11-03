import pytest
from services.ods_api_service import OdsApiService
from tests.unit.helpers.data.ods.utils import load_ods_response_data
from tests.unit.helpers.mock_response import MockResponse
from utils.exceptions import OdsErrorException, OrganisationNotFoundException


def test_fetch_organisation_data_valid_returns_organisation_data(mocker):
    test_ods_code = "X26"
    ord_api_request_url = f"https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/{test_ods_code}"
    expected = """{"successfulJSONResponse"}"""
    response_200 = MockResponse(200, {expected})
    mock_api = mocker.patch("requests.get", return_value=response_200)

    actual = OdsApiService.fetch_organisation_data(test_ods_code)

    assert actual == expected
    assert mock_api.assert_called_with(ord_api_request_url)


def test_fetch_organisation_data_404_raise_OrganisationNotFoundException(mocker):
    response_404 = MockResponse(404, {"errorCode": 404, "errorText": "Not found"})

    mocker.patch("requests.get", return_value=response_404)
    with pytest.raises(OrganisationNotFoundException):
        OdsApiService.fetch_organisation_data("non-exist-ods-code")


def test_fetch_organisation_data_catch_all_raises_OdsErrorException(mocker):
    response_400 = MockResponse(400, "BadRequest")

    mocker.patch("requests.get", return_value=response_400)

    with pytest.raises(OdsErrorException):
        OdsApiService.fetch_organisation_data("bad-ods-code")


@pytest.fixture()
def mock_ods_responses():
    # load test data from several json files and pass to below tests in a dict
    yield load_ods_response_data()

def test_parse_ods_response_extracts_data_and_includes_role_code_passed_as_arg(
    mock_ods_responses,
):
    test_response = mock_ods_responses["pcse_role"]
    role_code = "this should be the role code and not the one in the mock data"

    actual = OdsApiService.parse_ods_response(test_response, role_code)
    expected = ("PORTWAY LIFESTYLE CENTRE", "A9A5A", role_code)

    assert actual == expected

    #TODO: fetch_organisation_with_permitted_role, find_and_get_gpp_org_code, find_and_get_pcse_ods
