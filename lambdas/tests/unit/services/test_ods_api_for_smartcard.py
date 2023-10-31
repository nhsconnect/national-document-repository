import pytest
from services.ods_api_service_for_smartcard import is_gpp_org
from tests.unit.helpers.data.ods.utils import load_ods_response_data


@pytest.fixture()
def mock_ods_responses():
    # load test data from several json files and pass to below tests in a dict
    yield load_ods_response_data()


def skip_test_is_gpp_org_returns_true_with_gp_details(mock_ods_responses):
    actual = is_gpp_org(mock_ods_responses["with_valid_gp_role"])
    expected = True

    assert actual == expected


def skip_test_is_gpp_org_returns_false_with_none_gp_details(mock_ods_responses):
    actual = is_gpp_org(mock_ods_responses["with_no_valid_roles"])
    expected = False

    assert actual == expected
