from unittest.mock import patch

import pytest

from services.oidc_service import OidcService
from utils.exceptions import AuthorisationException

MOCK_PARAMETERS = {
    "OIDC_CLIENT_ID": "mock_client_id",
    "OIDC_CLIENT_SECRET": "mock_client_secret",
    "OIDC_ISSUER_URL": "https://localhost:3000/mock_issuer_url",
    "OIDC_TOKEN_URL": "https://localhost:3000/mock_token_url",
    "OIDC_USER_INFO_URL": "https://localhost:3000/mock_userinfo_url",
    "OIDC_CALLBACK_URL": "https://localhost:3000/mock_callback_url",
}


@pytest.fixture
def oidc_service():
    with patch.object(OidcService, "fetch_oidc_parameters") as mock_fetch_parameters:
        mock_fetch_parameters.return_value(MOCK_PARAMETERS)
        oidc_service = OidcService()
        yield oidc_service


class MockResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self.json_data = json_data

    def json(self):
        return self.json_data

    def content(self):
        return repr(self.json_data)


def test_oidc_service_fetch_the_access_token(mocker, oidc_service):
    auth_code = "fake_auth_code"
    expected = "mock_access_token"
    mock_response = MockResponse(
        status_code=200,
        json_data={
            "access_token": expected,
            "scope": "openid",
            "id_token": "fake_id_token",
            "token_type": "Bearer",
            "expires_in": 3599,
        },
    )

    mocker.patch("requests.post", return_value=mock_response)

    actual = oidc_service.fetch_access_token(auth_code)

    assert actual == expected


def test_oidc_service_fetch_the_access_token_raises_AuthorisationException_for_invalid_auth_code(
    mocker, oidc_service
):
    mocker.patch(
        "requests.post",
        return_value=MockResponse(
            400,
            {
                "error_description": "The provided access grant is invalid, expired, or revoked.",
                "error": "invalid_grant",
            },
        ),
    )

    with pytest.raises(AuthorisationException):
        oidc_service.fetch_access_token("invalid_auth_code")


def test_oidc_service_fetch_user_org_codes(mocker, oidc_service):
    mock_token = "fake_access_token"
    mock_userinfo = {
        "nhsid_useruid": "500000000000",
        "name": "TestUserOne Caius Mr",
        "nhsid_nrbac_roles": [
            {
                "person_orgid": "500000000000",
                "person_roleid": "500000000000",
                "org_code": "A9A5A",
                "role_name": '"Support":"Systems Support":"Systems Support Access Role"',
                "role_code": "S8001:G8005:R8015",
            },
            {
                "person_orgid": "500000000000",
                "person_roleid": "500000000000",
                "org_code": "B9A5A",
                "role_name": '"Primary Care Support England":"Systems Support Access Role"',
                "role_code": "S8001:G8005:R8015",
            },
        ],
        "given_name": "Caius",
        "family_name": "TestUserOne",
        "uid": "500000000000",
        "nhsid_user_orgs": [
            {"org_name": "NHSID DEV", "org_code": "A9A5A"},
            {"org_name": "Primary Care Support England", "org_code": "B9A5A"},
        ],
        "sub": "500000000000",
    }

    expected = ["A9A5A", "B9A5A"]

    mock_response = MockResponse(status_code=200, json_data=mock_userinfo)

    mocker.patch("requests.get", return_value=mock_response)

    actual = oidc_service.fetch_user_org_codes(mock_token)
    assert actual == expected


def test_oidc_service_fetch_user_org_codes_raise_AuthorisationException(
    mocker, oidc_service
):
    mock_token = "fake_access_token"

    mock_response = MockResponse(
        status_code=401,
        json_data={
            "error_description": "The access token provided is expired, revoked, malformed, or invalid for other reasons.",
            "error": "invalid_token",
        },
    )
    mocker.patch("requests.get", return_value=mock_response)

    with pytest.raises(AuthorisationException):
        oidc_service.fetch_user_org_codes(mock_token)
