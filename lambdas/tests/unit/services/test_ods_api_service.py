import json

import pytest
from requests import Response
from services.ods_api_service import (
    OdsApiService,
    find_icb_for_user,
    parse_ods_response,
)
from services.token_handler_ssm_service import TokenHandlerSSMService
from tests.unit.helpers.data.ods.ods_organisation_response import (
    NO_RELS_RESPONSE,
    ORGANISATION_RESPONSE,
    RE6_REL_ID_RESPONSE,
)
from tests.unit.helpers.data.ods.utils import load_ods_response_data
from tests.unit.helpers.mock_response import MockResponse
from utils.exceptions import (
    OdsErrorException,
    OrganisationNotFoundException,
    TooManyOrgsException,
)


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


def test_fetch_organisation_data_404_response_raises_exception(mocker):
    response_404 = MockResponse(404, {"errorCode": 404, "errorText": "Not found"})

    mocker.patch("requests.get", return_value=response_404)
    with pytest.raises(OrganisationNotFoundException):
        OdsApiService.fetch_organisation_data(OdsApiService(), "non-existent-ods-code")


def test_fetch_organisation_data_catch_all_raises_exception(mocker):
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

    actual = parse_ods_response(test_response, role_code, "Test_icb_code")
    expected = {
        "name": "Primary Care Support England",
        "org_ods_code": "X4S4L",
        "role_code": role_code,
        "icb_ods_code": "Test_icb_code",
    }

    assert actual == expected


def test_fetch_org_with_permitted_role_pcse(mock_ods_responses, mocker):
    mocker.patch.object(
        OdsApiService,
        "fetch_organisation_data",
        return_value=mock_ods_responses["pcse_org"],
    )
    mocker.patch.object(
        TokenHandlerSSMService, "get_pcse_ods_code", return_value=["X4S4L"]
    )
    pcse_ods = "X4S4L"
    expected = {
        "name": "Primary Care Support England",
        "org_ods_code": pcse_ods,
        "role_code": "",
        "icb_ods_code": "PCSE",
    }

    actual = OdsApiService.fetch_organisation_with_permitted_role(
        OdsApiService(), [pcse_ods]
    )

    assert expected == actual


def test_fetch_org_with_permitted_role_gp(mock_ods_responses, mocker):
    mocker.patch.object(
        OdsApiService,
        "fetch_organisation_data",
        return_value=mock_ods_responses["gp_org"],
    )
    mocker.patch.object(
        TokenHandlerSSMService, "get_gp_org_role_code", return_value="RO76"
    )
    mocker.patch.object(
        TokenHandlerSSMService, "get_pcse_ods_code", return_value=["X4S4L"]
    )
    gp_ods = "A9A5A"
    expected = {
        "name": "Mock GP Practice",
        "org_ods_code": "A9A5A",
        "role_code": "RO76",
        "icb_ods_code": "No ICB code found",
    }

    actual = OdsApiService.fetch_organisation_with_permitted_role(
        OdsApiService(), [gp_ods]
    )

    assert expected == actual


def test_fetch_org_with_permitted_role_returns_empty_list_when_not_gp_or_pcse(
    mock_ods_responses, mocker
):
    mocker.patch.object(
        OdsApiService,
        "fetch_organisation_data",
        return_value=mock_ods_responses["not_gp_or_pcse"],
    )
    mocker.patch.object(
        TokenHandlerSSMService, "get_gp_org_role_code", return_value="RO76"
    )
    mocker.patch.object(
        TokenHandlerSSMService, "get_pcse_ods_code", return_value=["X4S4L"]
    )
    ods = "OD5"
    expected = {}

    actual = OdsApiService.fetch_organisation_with_permitted_role(
        OdsApiService(), [ods]
    )

    assert expected == actual


def test_fetch_org_with_permitted_role_raises_exception_if_more_than_one_org_for_user(
    mock_ods_responses,
):
    with pytest.raises(TooManyOrgsException):
        OdsApiService.fetch_organisation_with_permitted_role(
            OdsApiService(), ["ods1", "ods2many"]
        )


@pytest.mark.parametrize(
    ["org_data", "expected"],
    [
        (RE6_REL_ID_RESPONSE, "No ICB code found"),
        (NO_RELS_RESPONSE, "No ICB code found"),
        (ORGANISATION_RESPONSE, "ICB_ODS_CODE"),
    ],
)
def test_find_org_relationship_icb_responses(org_data, expected):
    actual = find_icb_for_user(org_data)
    assert actual == expected
