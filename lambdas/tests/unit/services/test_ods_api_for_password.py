import pytest
from services.ods_api_service_for_password import OdsApiServiceForPassword
from tests.unit.helpers.data.ods.utils import load_ods_response_data
from tests.unit.helpers.mock_response import MockResponse
from utils.exceptions import OdsErrorException, OrganisationNotFoundException


def test_fetch_organisation_data_valid_returns_organisation_data():
    test_ods_code = "X26"

    actual = OdsApiServiceForPassword().fetch_organisation_data(test_ods_code)

    assert "NHS ENGLAND - X26" in str(actual)
    assert "PrimaryRoleId" in str(actual)


def test_fetch_organisation_data_404_raise_OrganisationNotFoundException(mocker):
    response_404 = MockResponse(404, {"errorCode": 404, "errorText": "Not found"})

    mocker.patch("requests.get", return_value=response_404)
    with pytest.raises(OrganisationNotFoundException):
        OdsApiServiceForPassword().fetch_organisation_data("non-exist-ods-code")


def test_fetch_organisation_data_catch_all_raises_OdsErrorException(mocker):
    response_400 = MockResponse(400, "BadRequest")

    mocker.patch("requests.get", return_value=response_400)
    invalid_ods_code = "!@?£?$?@?"

    with pytest.raises(OdsErrorException):
        OdsApiServiceForPassword().fetch_organisation_data(invalid_ods_code)


@pytest.fixture()
def mock_ods_responses():
    # load test data from several json files and pass to below tests in a dict
    yield load_ods_response_data()
