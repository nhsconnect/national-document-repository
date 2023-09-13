import pytest

from services.ods_api_service import OdsApiService
from utils.exceptions import OrganisationNotFoundException, OdsErrorException


def test_fetch_organisation_data_valid_returns_organisation_data():
    test_ods_code = "X26"

    actual = OdsApiService.fetch_organisation_data(test_ods_code)

    assert 'NHS ENGLAND - X26' in str(actual)
    assert 'PrimaryRoleId' in str(actual)

def test_fetch_organisation_data_404_raise_OrganisationNotFoundException():
    test_ods_code = "non-exist-ods-code"

    with pytest.raises(OrganisationNotFoundException):
        OdsApiService.fetch_organisation_data(test_ods_code)

def test_fetch_organisation_data_catch_all_raises_OdsErrorException():
    invalid_ods_code = "!@?£?$?@?"

    with pytest.raises(OdsErrorException):
        OdsApiService.fetch_organisation_data(invalid_ods_code)