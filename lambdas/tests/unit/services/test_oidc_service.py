import json
import time

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from models.oidc_models import IdTokenClaimSet
from requests import Response
from services.oidc_service import OidcService
from tests.unit.helpers.mock_response import MockResponse
from utils.exceptions import AuthorisationException, OidcApiException

MOCK_PARAMETERS = {
    "OIDC_CLIENT_ID": "mock_client_id",
    "OIDC_CLIENT_SECRET": "mock_client_secret",
    "OIDC_ISSUER_URL": "https://localhost:3000/mock_issuer_url",
    "OIDC_TOKEN_URL": "https://localhost:3000/mock_token_url",
    "OIDC_USER_INFO_URL": "https://localhost:3000/mock_userinfo_url",
    "OIDC_CALLBACK_URL": "https://localhost:3000/mock_callback_url",
    "OIDC_JWKS_URL": "https://localhost:3000/mock_jwks_url",
    "WORKSPACE" : "production"
}


@pytest.fixture
def oidc_service(mocker):
    oidc_service = OidcService()
    mocker.patch.object(
        oidc_service, "fetch_oidc_parameters", return_value=MOCK_PARAMETERS
    )
    oidc_service.set_up_oidc_parameters(FakeSSMService, FakeWebAppClient)
    yield oidc_service


class FakeWebAppClient:
    def __init__(self, *arg, **kwargs):
        self.state = "test1state"

    @staticmethod
    def prepare_token_request(*args, **kwargs):
        return "test", "", ""


class FakeSSMService:
    def __init__(self, *arg, **kwargs):
        self.state = "test1state"


def test_fetch_tokens_successfully(mocker, oidc_service):
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
        "selected_roleid": "012345678901",
        "acr": "AAL3",
    }

    mocker.patch("requests.post", return_value=mock_cis2_response)
    mocked_id_token_validation = mocker.patch.object(
        oidc_service, "validate_and_decode_token", return_value=mock_decoded_claim_set
    )

    expected = (mock_access_token, IdTokenClaimSet(**mock_decoded_claim_set))

    actual = oidc_service.fetch_tokens("test_auth_code")

    assert actual == expected
    mocked_id_token_validation.assert_called_with(mock_id_token)


def test_fetch_tokens_raises_exception_for_invalid_auth_code(mocker, oidc_service):
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

    with pytest.raises(OidcApiException):
        oidc_service.fetch_tokens("invalid_auth_code")


def test_fetch_tokens_raises_AuthorisationException_for_invalid_id_token(
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
        oidc_service,
        "validate_and_decode_token",
        side_effect=AuthorisationException(),
    )

    with pytest.raises(AuthorisationException):
        oidc_service.fetch_tokens("test_auth_code")


def test_fetch_user_org_code(mocker, oidc_service, mock_userinfo):
    mock_access_token = "fake_access_token"

    mock_decoded_claim_set = {
        "sid": "fake_cis2_session_id",
        "sub": "fake_cis2_login_id",
        "exp": 1234567890,
        "selected_roleid": mock_userinfo["role_id"],
    }

    mock_response = MockResponse(status_code=200, json_data=mock_userinfo["user_info"])

    mocker.patch("requests.get", return_value=mock_response)

    actual = oidc_service.fetch_user_org_codes(
        mock_access_token, IdTokenClaimSet(**mock_decoded_claim_set)
    )
    assert actual[0] == mock_userinfo["org_code"]


def test_fetch_user_org_codes_raises_exception_for_invalid_access_token(
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

    with pytest.raises(OidcApiException):
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
        "acr": "AAL3"
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


def test_validate_and_decode_token_validate_token_with_proper_keys(
    mock_id_tokens, oidc_service, mock_jwk_client
):
    id_token = mock_id_tokens["valid_id_token"]

    actual = oidc_service.validate_and_decode_token(id_token)
    expect = mock_id_tokens["expected_claim_set"]

    assert actual == expect


def test_validate_and_decode_token_raises_exception_for_fake_id_token(
    mock_id_tokens, oidc_service, mock_jwk_client
):
    counterfeit_id_token = mock_id_tokens["counterfeit_id_token"]

    with pytest.raises(OidcApiException):
        oidc_service.validate_and_decode_token(counterfeit_id_token)


def test_oidc_service_validate_and_decode_token_raises_exception_for_expired_id_token(
    mock_id_tokens, oidc_service, mock_jwk_client
):
    expired_id_token = mock_id_tokens["expired_id_token"]

    with pytest.raises(OidcApiException):
        oidc_service.validate_and_decode_token(expired_id_token)


def test_parse_fetch_tokens_response(mocker, oidc_service, mock_id_tokens):
    mock_access_token = "mock_access_token"
    mock_id_token = {"acr": "AAL3"}
    mock_cis2_response = Response()
    mock_cis2_response.status_code = 200
    mock_cis2_response._content = json.dumps(
        {
            "access_token": mock_access_token,
            "scope": "openid",
            "id_token": mock_id_token,
            "token_type": "Bearer",
            "expires_in": 3599,
        }
    ).encode("utf-8")

    mock_decoded_token = {"token_field": "mock_content"}
    mock_decoder = mocker.patch.object(
        OidcService, "validate_and_decode_token", return_value=mock_decoded_token
    )
    mock_id_token_claimset = mocker.patch.object(
        IdTokenClaimSet, "model_validate", return_value=mock_id_token
    )

    (
        actual_access_token,
        actual_id_token_claims_set,
    ) = oidc_service.parse_fetch_tokens_response(mock_cis2_response)

    assert actual_access_token == mock_access_token
    assert actual_id_token_claims_set == mock_id_token
    mock_decoder.assert_called_with(mock_id_token)
    mock_id_token_claimset.assert_called_with(mock_decoded_token)


def test_fetch_tokens_response_throws_authorisation_exception_when_access_token_is_missing(
    oidc_service,
):
    mock_cis2_response = Response()
    mock_cis2_response.status_code = 200
    mock_cis2_response._content = json.dumps(
        {
            "scope": "openid",
            "token_type": "Bearer",
            "expires_in": 3599,
        }
    ).encode("utf-8")

    with pytest.raises(OidcApiException):
        oidc_service.parse_fetch_tokens_response(mock_cis2_response)


def test_fetch_user_role_code(oidc_service, mock_userinfo, mock_id_tokens, mocker):
    mock_access_token = "access_token"
    mock_claim_set = "mock_claim_set"
    prefix_char = "R"

    mock_fetch_userinfo = mocker.patch.object(
        OidcService, "fetch_userinfo", return_value=mock_userinfo["user_info"]
    )
    mock_oidc_get_selected_role = mocker.patch(
        "services.oidc_service.get_selected_roleid",
        return_value=mock_userinfo["role_id"],
    )

    expected = (mock_userinfo["role_code"], mock_userinfo["user_id"])

    actual = oidc_service.fetch_user_role_code(
        mock_access_token, mock_claim_set, prefix_char
    )

    assert actual == expected
    mock_fetch_userinfo.assert_called_once()
    mock_oidc_get_selected_role.assert_called_once()


def test_fetch_user_role_code_raises_auth_exception_if_no_role_codes(
    oidc_service, mock_userinfo, mock_id_tokens, mocker
):
    mock_access_token = "access_token"
    mock_claim_set = "mock_claim_set"
    prefix_char = "R"

    mock_fetch_userinfo = mocker.patch.object(
        OidcService, "fetch_userinfo", return_value=mock_userinfo["user_info"]
    )
    mock_oidc_get_selected_role = mocker.patch(
        "services.oidc_service.get_selected_roleid", return_value="not_in_data"
    )

    with pytest.raises(AuthorisationException):
        oidc_service.fetch_user_role_code(
            mock_access_token, mock_claim_set, prefix_char
        )

    mock_fetch_userinfo.assert_called_once()
    mock_oidc_get_selected_role.assert_called_once()


def test_fetch_user_role_code_raises_auth_exception_if_no_role_codes_with_specified_prefix(
    oidc_service, mock_userinfo, mock_id_tokens, mocker
):
    mock_access_token = "access_token"
    mock_claim_set = "mock_claim_set"
    prefix_char = "invalid_prefix"

    mock_fetch_userinfo = mocker.patch.object(
        OidcService, "fetch_userinfo", return_value=mock_userinfo["user_info"]
    )
    mock_oidc_get_selected_role = mocker.patch(
        "services.oidc_service.get_selected_roleid",
        return_value=mock_userinfo["role_id"],
    )

    with pytest.raises(AuthorisationException):
        oidc_service.fetch_user_role_code(
            mock_access_token, mock_claim_set, prefix_char
        )

    mock_fetch_userinfo.assert_called_once()
    mock_oidc_get_selected_role.assert_called_once()


def test_fetch_user_info(oidc_service, mocker, mock_userinfo):
    mock_response = MockResponse(status_code=200, json_data=mock_userinfo["user_info"])
    mocker.patch("requests.get", return_value=mock_response)
    mock_token = "access_token"
    actual = oidc_service.fetch_userinfo(mock_token)

    assert actual == mock_userinfo["user_info"]


def test_fetch_user_info_throws_exception_for_non_200_response(oidc_service, mocker):
    mock_response = MockResponse(status_code=400, json_data="")
    mocker.patch("requests.get", return_value=mock_response)

    with pytest.raises(OidcApiException):
        oidc_service.fetch_userinfo("access_token")
