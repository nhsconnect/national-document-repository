import time
from unittest.mock import patch

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from models.oidc_models import IdTokenClaimSet
from services.oidc_service import OidcService
from tests.unit.helpers.mock_response import MockResponse
from utils.exceptions import AuthorisationException

MOCK_PARAMETERS = {
    "OIDC_CLIENT_ID": "mock_client_id",
    "OIDC_CLIENT_SECRET": "mock_client_secret",
    "OIDC_ISSUER_URL": "https://localhost:3000/mock_issuer_url",
    "OIDC_TOKEN_URL": "https://localhost:3000/mock_token_url",
    "OIDC_USER_INFO_URL": "https://localhost:3000/mock_userinfo_url",
    "OIDC_CALLBACK_URL": "https://localhost:3000/mock_callback_url",
    "OIDC_JWKS_URL": "https://localhost:3000/mock_jwks_url",
}


@pytest.fixture
def oidc_service(mocker):
    with patch.object(
        OidcService, "fetch_oidc_parameters", return_value=MOCK_PARAMETERS
    ):
        oidc_service = OidcService()
        yield oidc_service


def test_oidc_service_fetch_tokens_successfully(mocker, oidc_service):
    mock_access_token = "mock_access_token"
    mock_id_token = "mock_id_token"
    mock_cis2_response = MockResponse(
        status_code=200,
        json_data={
            "access_token": mock_access_token,
            "scope": "openid",
            "id_token": mock_id_token,
            "token_type": "Bearer",
            "expires_in": 3599,
        },
    )
    mock_decoded_claim_set = {
        "sid": "fake_cis2_session_id",
        "sub": "fake_cis2_login_id",
        "exp": 1234567890,
        "selected_roleid": "012345678901"
    }

    mocker.patch("requests.post", return_value=mock_cis2_response)
    mocked_id_token_validation = mocker.patch.object(
        oidc_service, "validate_and_decode_token", return_value=mock_decoded_claim_set
    )

    expected = (mock_access_token, IdTokenClaimSet(**mock_decoded_claim_set))

    actual = oidc_service.fetch_tokens("test_auth_code")

    assert actual == expected
    mocked_id_token_validation.assert_called_with(mock_id_token)


def test_oidc_service_fetch_tokens_raises_AuthorisationException_for_invalid_auth_code(
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
        oidc_service.fetch_tokens("invalid_auth_code")


def test_oidc_service_fetch_tokens_raises_AuthorisationException_for_invalid_id_token(
    mocker, oidc_service
):
    mock_access_token = "mock_access_token"
    invalid_id_token = "invalid_id_token"
    mock_cis2_response = MockResponse(
        status_code=200,
        json_data={
            "access_token": mock_access_token,
            "scope": "openid",
            "id_token": invalid_id_token,
            "token_type": "Bearer",
            "expires_in": 3599,
        },
    )
    mocker.patch("requests.post", return_value=mock_cis2_response)
    mocker.patch.object(
        oidc_service, "validate_and_decode_token", side_effect=AuthorisationException
    )

    with pytest.raises(AuthorisationException):
        oidc_service.fetch_tokens("test_auth_code")


def test_oidc_service_fetch_user_org_code(mocker, oidc_service):
    mock_access_token = "fake_access_token"
    role_id = "500000000001"
    expected_ods_code = "A9A5A"
    mock_userinfo = {
        "nhsid_useruid": "500000000000",
        "name": "TestUserOne Caius Mr",
        "nhsid_nrbac_roles": [
            {
                "person_orgid": "500000000000",
                "person_roleid": role_id,
                "org_code": expected_ods_code,
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

    mock_decoded_claim_set = {
        "sid": "fake_cis2_session_id",
        "sub": "fake_cis2_login_id",
        "exp": 1234567890,
        "selected_roleid": role_id
    }

    mock_response = MockResponse(status_code=200, json_data=mock_userinfo)

    mocker.patch("requests.get", return_value=mock_response)

    actual = oidc_service.fetch_user_org_codes(mock_access_token, IdTokenClaimSet(**mock_decoded_claim_set))
    assert actual[0] == expected_ods_code


def test_oidc_service_fetch_user_org_codes_raise_AuthorisationException_for_invalid_access_token(
    mocker, oidc_service
):
    mock_token = "fake_access_token"

    mock_response = MockResponse(
        status_code=401,
        json_data={
            "error_description": "The access token provided is expired, revoked, "
            "malformed, or invalid for other reasons.",
            "error": "invalid_token",
        },
    )
    mocker.patch("requests.get", return_value=mock_response)

    with pytest.raises(AuthorisationException):
        oidc_service.fetch_user_org_codes(mock_token, "not a real role")


@pytest.fixture(name="mock_id_tokens", scope="session")
def mock_cis2_public_key_and_id_tokens():
    mock_cis2_private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=4096
    )
    mock_cis2_public_key = mock_cis2_private_key.public_key()

    claim_set = {
        "name": "fake_id_token",
        "iss": MOCK_PARAMETERS["OIDC_ISSUER_URL"],
        "aud": MOCK_PARAMETERS["OIDC_CLIENT_ID"],
        "exp": time.time() + 3600,
    }
    valid_id_token = jwt.encode(claim_set, key=mock_cis2_private_key, algorithm="RS256")

    fake_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    id_token_of_fake_key = jwt.encode(claim_set, key=fake_key, algorithm="RS256")

    one_minute_ago = time.time() - 60
    valid_id_token_but_expired = jwt.encode(
        {**claim_set, "exp": one_minute_ago},
        key=mock_cis2_private_key,
        algorithm="RS256",
    )

    yield {
        "valid_id_token": valid_id_token,
        "counterfeit_id_token": id_token_of_fake_key,
        "expected_claim_set": claim_set,
        "expired_id_token": valid_id_token_but_expired,
        "mock_cis2_public_key": mock_cis2_public_key,
    }


@pytest.fixture()
def mock_jwk_client(mocker, mock_id_tokens):
    # jwk client normally will fetch the public key from cis2 server. mock it with our fake public key instead.
    mock_cis2_signing_key = mocker.Mock()
    mock_cis2_signing_key.key = mock_id_tokens["mock_cis2_public_key"]
    mocker.patch.object(
        jwt.PyJWKClient, "get_signing_key_from_jwt", return_value=mock_cis2_signing_key
    )
    yield


def test_oidc_service_validate_and_decode_token__validate_token_with_proper_keys(
    mock_id_tokens, oidc_service, mock_jwk_client
):
    id_token = mock_id_tokens["valid_id_token"]

    actual = oidc_service.validate_and_decode_token(id_token)
    expect = mock_id_tokens["expected_claim_set"]

    assert actual == expect


def test_oidc_service_validate_and_decode_token_raise_AuthorisationException_for_fake_id_token(
    mock_id_tokens, oidc_service, mock_jwk_client
):
    counterfeit_id_token = mock_id_tokens["counterfeit_id_token"]

    with pytest.raises(AuthorisationException):
        oidc_service.validate_and_decode_token(counterfeit_id_token)


def test_oidc_service_validate_and_decode_token_raise_AuthorisationException_for_expired_id_token(
    mock_id_tokens, oidc_service, mock_jwk_client
):
    expired_id_token = mock_id_tokens["expired_id_token"]

    with pytest.raises(AuthorisationException):
        oidc_service.validate_and_decode_token(expired_id_token)
