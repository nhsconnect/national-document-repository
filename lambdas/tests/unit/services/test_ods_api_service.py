import pytest
from enums.permitted_role import PermittedRole
from services.ods_api_service import OdsApiService
from tests.unit.helpers.data.ods.utils import load_ods_response_data
from tests.unit.helpers.mock_response import MockResponse
from utils.exceptions import OdsErrorException, OrganisationNotFoundException


def test_fetch_organisation_data_valid_returns_organisation_data():
    test_ods_code = "X26"

    actual = OdsApiService.fetch_organisation_data(test_ods_code)

    assert "NHS ENGLAND - X26" in str(actual)
    assert "PrimaryRoleId" in str(actual)


def test_fetch_organisation_data_404_raise_OrganisationNotFoundException(mocker):
    response_404 = MockResponse(404, {"errorCode": 404, "errorText": "Not found"})

    mocker.patch("requests.get", return_value=response_404)
    with pytest.raises(OrganisationNotFoundException):
        OdsApiService.fetch_organisation_data("non-exist-ods-code")


def test_fetch_organisation_data_catch_all_raises_OdsErrorException(mocker):
    response_400 = MockResponse(400, "BadRequest")

    mocker.patch("requests.get", return_value=response_400)
    invalid_ods_code = "!@?£?$?@?"

    with pytest.raises(OdsErrorException):
        OdsApiService.fetch_organisation_data(invalid_ods_code)


@pytest.fixture()
def mock_ods_responses():
    # load test data from several json files and pass to below tests in a dict
    yield load_ods_response_data()


def skip_test_parse_ods_response_extract_organisation_with_permitted_gp_role(
    mock_ods_responses,
):
    test_response = mock_ods_responses["with_valid_gp_role"]

    actual = OdsApiService.parse_ods_response(test_response)
    expect = ("PORTWAY LIFESTYLE CENTRE", "A9A5A", PermittedRole.GP.name)

    assert actual == expect


def test_parse_ods_response_extract_organisation_with_permitted_PCSE_role(
    mock_ods_responses,
):
    test_response = mock_ods_responses["with_valid_pcse_role"]

    actual = OdsApiService.parse_ods_response(test_response)
    expect = ("Primary Care Support England", "B9A5A", PermittedRole.PCSE.name)

    assert actual == expect


def skip_test_parse_ods_response_return_the_first_valid_role_if_more_than_one_exists(
    mock_ods_responses,
):
    test_response = mock_ods_responses["with_multiple_valid_roles"]

    actual = OdsApiService.parse_ods_response(test_response)
    expect = ("PORTWAY LIFESTYLE CENTRE", "A9A5A", PermittedRole.GP.name)

    assert actual == expect


def test_parse_ods_response_should_return_none_if_no_valid_role_was_found(
    mock_ods_responses,
):
    test_response = mock_ods_responses["with_no_valid_roles"]

    actual = OdsApiService.parse_ods_response(test_response)
    expect = None

    assert actual == expect
