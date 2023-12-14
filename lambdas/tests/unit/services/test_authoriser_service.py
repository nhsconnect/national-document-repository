import pytest
from enums.repository_role import RepositoryRole
from services.authoriser_service import AuthoriserService
from services.base.dynamo_service import DynamoDBService
from utils.exceptions import AuthorisationException

MOCK_METHOD_ARN_PREFIX = "arn:aws:execute-api:eu-west-2:74747474747474:<<restApiId>/dev"
TEST_PUBLIC_KEY = "test_public_key"
DENY_ALL_POLICY = {
    "Statement": [
        {
            "Action": "execute-api:Invoke",
            "Effect": "Deny",
            "Resource": [f"{MOCK_METHOD_ARN_PREFIX}/*/*"],
        }
    ],
    "Version": "2012-10-17",
}
MOCK_SESSION_ID = "test_session_id"
MOCK_CURRENT_SESSION = {
    "NDRSessionId": MOCK_SESSION_ID,
    "sid": "test_cis2_session_id",
    "Subject": "test_cis2_user_id",
    "TimeToExist": 12345678960,
}


@pytest.fixture(scope="function")
def mock_auth_service():
    mock_test_auth_service = AuthoriserService()
    yield mock_test_auth_service


@pytest.fixture()
def mock_dynamo_service(mocker):
    valid_session_record = {
        "Count": 1,
        "Items": [
            {
                "NDRSessionId": "test_session_id",
                "sid": "test_cis2_session_id",
                "Subject": "test_cis2_user_id",
                "TimeToExist": 12345678960,
            }
        ],
    }
    dynamo_service = mocker.patch.object(DynamoDBService, "simple_query")
    dynamo_service.return_value = valid_session_record
    yield dynamo_service


def build_decoded_token_for_role(role: str) -> dict:
    return {
        "exp": 12345678960,
        "iss": "nhs repo",
        "smart_card_role": "temp_mock_role",
        "selected_organisation": {
            "name": "PORTWAY LIFESTYLE CENTRE",
            "org_ods_code": "A9A5A",
            "role": "temp_role",
        },
        "repository_role": role,
        "ndr_session_id": "test_session_id",
    }


@pytest.fixture
def mock_jwt_decode(mocker):
    def mocked_decode_method(auth_token: str, *_args, **_kwargs):
        if auth_token == "valid_gp_admin_token":
            return build_decoded_token_for_role(RepositoryRole.GP_ADMIN.name)
        elif auth_token == "valid_gp_clinical_token":
            return build_decoded_token_for_role(RepositoryRole.GP_CLINICAL.name)
        elif auth_token == "valid_pcse_token":
            return build_decoded_token_for_role(RepositoryRole.PCSE.name)
        else:
            return None

    yield mocker.patch(
        "services.token_service.TokenService.get_public_key_and_decode_auth_token",
        side_effect=mocked_decode_method,
    )


@pytest.mark.parametrize(
    "test_path", ["/DocumentManifest", "/DocumentDelete", "/DocumentReference"]
)
def test_deny_access_policy_returns_true_for_gp_clinical_on_paths(
    test_path,
    mock_auth_service: AuthoriserService,
):
    expected = True
    actual = mock_auth_service.deny_access_policy(
        test_path, RepositoryRole.GP_CLINICAL.value
    )
    assert expected == actual


def test_deny_access_policy_returns_false_for_gp_clinical_on_search_path(
    mock_auth_service: AuthoriserService,
):
    expected = False
    actual = mock_auth_service.deny_access_policy(
        "/SearchPatient", RepositoryRole.GP_CLINICAL.value
    )
    assert expected == actual


@pytest.mark.parametrize(
    "test_path",
    ["/DocumentManifest", "/DocumentDelete", "/DocumentReference", "/SearchPatient"],
)
def test_deny_access_policy_returns_false_for_pcse_on_all_paths(
    test_path,
    mock_auth_service: AuthoriserService,
):
    expected = False
    actual = mock_auth_service.deny_access_policy(test_path, RepositoryRole.PCSE.value)
    assert expected == actual


def test_deny_access_policy_returns_false_for_unrecognised_path(
    mock_auth_service: AuthoriserService,
):
    expected = False

    actual = mock_auth_service.deny_access_policy("/test", RepositoryRole.PCSE.value)

    assert expected == actual


def test_find_login_session(
    set_env, mock_dynamo_service, mock_auth_service: AuthoriserService
):
    expected = MOCK_CURRENT_SESSION
    actual = mock_auth_service.find_login_session(MOCK_SESSION_ID)

    assert expected == actual


def test_find_login_session_raises_auth_exception(
    mocker, set_env, mock_auth_service: AuthoriserService
):
    invalid_session_record = {
        "Count": 1,
    }
    dynamo_service = mocker.patch.object(DynamoDBService, "simple_query")
    dynamo_service.return_value = invalid_session_record

    with pytest.raises(AuthorisationException):
        mock_auth_service.find_login_session("test session id")


def test_validate_login_session(mocker, mock_auth_service: AuthoriserService):
    mocker.patch("time.time", return_value=2400000)
    try:
        mock_auth_service.validate_login_session(session_expiry_time=3400000)
    except AuthorisationException:
        assert False, "test"


def test_validate_login_expired_session(mocker, mock_auth_service: AuthoriserService):
    mocker.patch("time.time", return_value=2400000)
    with pytest.raises(AuthorisationException):
        mock_auth_service.validate_login_session(session_expiry_time=1400000)


@pytest.mark.parametrize("path_test", ["/DocumentManifest"])
def test_valid_gp_admin_token_returns_allow_policy_true(
    path_test, mock_jwt_decode, mocker, mock_auth_service: AuthoriserService
):
    auth_token = "valid_gp_admin_token"

    mock_find_login_session = mocker.patch(
        "services.authoriser_service.AuthoriserService.find_login_session",
        return_value=MOCK_CURRENT_SESSION,
    )
    mock_validate_login_session = mocker.patch(
        "services.authoriser_service.AuthoriserService.validate_login_session",
        return_value=True,
    )
    mock_deny_access_policy = mocker.patch(
        "services.authoriser_service.AuthoriserService.deny_access_policy",
        return_value=False,
    )

    response = mock_auth_service.auth_request(path_test, "test public key", auth_token)

    mock_jwt_decode.assert_called_with(
        auth_token=auth_token, ssm_public_key_parameter="test public key"
    )
    assert response
    mock_find_login_session.assert_called_once()
    mock_validate_login_session.assert_called_once()
    mock_deny_access_policy.assert_called_once()


@pytest.mark.parametrize("test_path", ["/SearchPatient"])
def test_valid_pcse_token_return_allow_policy_true(
    test_path, mocker, mock_jwt_decode, mock_auth_service: AuthoriserService
):
    auth_token = "valid_pcse_token"

    mock_find_login_session = mocker.patch(
        "services.authoriser_service.AuthoriserService.find_login_session",
        return_value=MOCK_CURRENT_SESSION,
    )
    mock_validate_login_session = mocker.patch(
        "services.authoriser_service.AuthoriserService.validate_login_session"
    )
    mock_deny_access_policy = mocker.patch(
        "services.authoriser_service.AuthoriserService.deny_access_policy",
        return_value=False,
    )

    response = mock_auth_service.auth_request(test_path, "test public key", auth_token)

    mock_jwt_decode.assert_called_with(
        auth_token=auth_token, ssm_public_key_parameter="test public key"
    )
    assert response
    mock_find_login_session.assert_called_once()
    mock_validate_login_session.assert_called_once()
    mock_deny_access_policy.assert_called_once()


@pytest.mark.parametrize("test_path", ["/SearchPatient"])
def test_return_deny_policy_when_no_session_found(
    test_path, mocker, mock_jwt_decode, mock_auth_service: AuthoriserService
):
    auth_token = "valid_pcse_token"

    mock_find_login_session = mocker.patch(
        "services.authoriser_service.AuthoriserService.find_login_session",
        side_effect=AuthorisationException(),
    )
    mock_validate_login_session = mocker.patch(
        "services.authoriser_service.AuthoriserService.validate_login_session"
    )
    mock_deny_access_policy = mocker.patch(
        "services.authoriser_service.AuthoriserService.deny_access_policy"
    )
    with pytest.raises(AuthorisationException):
        mock_auth_service.auth_request(test_path, "test public key", auth_token)

        mock_jwt_decode.assert_called_with(
            auth_token=auth_token, ssm_public_key_parameter="test public key"
        )
        mock_find_login_session.assert_called_once()
        mock_validate_login_session.assert_not_called()
        mock_deny_access_policy.assert_not_called()


@pytest.mark.parametrize("test_path", ["/SearchPatient"])
def test_raise_exception_when_user_session_is_expired(
    test_path,
    mocker,
    mock_auth_service: AuthoriserService,
    mock_jwt_decode,
):
    auth_token = "valid_pcse_token"

    mock_find_login_session = mocker.patch(
        "services.authoriser_service.AuthoriserService.find_login_session",
        return_value=MOCK_CURRENT_SESSION,
    )
    mock_validate_login_session = mocker.patch(
        "services.authoriser_service.AuthoriserService.validate_login_session",
        side_effect=AuthorisationException(),
    )
    mock_deny_access_policy = mocker.patch(
        "services.authoriser_service.AuthoriserService.deny_access_policy"
    )
    with pytest.raises(AuthorisationException):
        mock_auth_service.auth_request(test_path, "test public key", auth_token)

    mock_jwt_decode.assert_called_with(
        auth_token=auth_token, ssm_public_key_parameter="test public key"
    )
    mock_find_login_session.assert_called_once()
    mock_validate_login_session.assert_called_once()
    mock_deny_access_policy.assert_not_called()


@pytest.mark.parametrize("test_path", ["/SearchPatient"])
def test_invalid_token_raise_exception(
    test_path, mocker, mock_jwt_decode, mock_auth_service: AuthoriserService
):
    auth_token = "invalid_token"

    mock_find_login_session = mocker.patch(
        "services.authoriser_service.AuthoriserService.find_login_session"
    )
    mock_validate_login_session = mocker.patch(
        "services.authoriser_service.AuthoriserService.validate_login_session"
    )
    mock_deny_access_policy = mocker.patch(
        "services.authoriser_service.AuthoriserService.deny_access_policy"
    )
    with pytest.raises(AuthorisationException):
        mock_auth_service.auth_request(test_path, "test public key", auth_token)

    mock_jwt_decode.assert_called_with(
        auth_token=auth_token, ssm_public_key_parameter="test public key"
    )
    mock_find_login_session.assert_not_called()
    mock_validate_login_session.assert_not_called()
    mock_deny_access_policy.assert_not_called()
