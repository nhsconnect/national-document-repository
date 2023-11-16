import time

import jwt
import pytest
from enums.repository_role import RepositoryRole
from handlers.authoriser_handler import lambda_handler, validate_access_policy

MOCK_METHOD_ARN_PREFIX = "arn:aws:execute-api:eu-west-2:fake_arn:fake_api_endpoint/dev"
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


@pytest.fixture()
def mock_ssm(set_env, mocker):
    mock_ssm_client = mocker.patch("boto3.client")
    mock_ssm_client.return_value.get_parameter.return_value = {
        "Parameter": {"Value": TEST_PUBLIC_KEY}
    }


@pytest.fixture()
def mock_session_table(mocker):
    mock_table = mocker.MagicMock()
    mock_dynamo = mocker.patch("boto3.resource")
    mock_dynamo.return_value.Table.return_value = mock_table

    valid_session_record = {
        "Count": 1,
        "Items": [
            {
                "NDRSessionId": "test_session_id",
                "sid": "test_cis2_session_id",
                "Subject": "test_cis2_user_id",
                "TimeToExist": time.time() + 60,
            }
        ],
    }
    mock_table.query.return_value = valid_session_record
    yield mock_table


def build_decoded_token_for_role(role: str) -> dict:
    return {
        "exp": time.time() + 60,
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
    def mocked_decode_method(token: str, *_args, **_kwargs):
        if token == "valid_gp_admin_token":
            return build_decoded_token_for_role(RepositoryRole.GP_ADMIN.name)
        elif token == "valid_gp_clinical_token":
            return build_decoded_token_for_role(RepositoryRole.GP_CLINICAL.name)
        elif token == "valid_pcse_token":
            return build_decoded_token_for_role(RepositoryRole.PCSE.name)
        else:
            raise jwt.exceptions.InvalidTokenError

    yield mocker.patch("jwt.decode", side_effect=mocked_decode_method)


def test_valid_gp_admin_token_return_allow_policy(
    mock_ssm, mock_session_table, mock_jwt_decode, context
):
    expected_allow_policy = {
        "Statement": [
            {
                "Action": "execute-api:Invoke",
                "Effect": "Allow",
                "Resource": [f"{MOCK_METHOD_ARN_PREFIX}/GET/SearchDocumentReferences"],
            }
        ],
        "Version": "2012-10-17",
    }

    auth_token = "valid_gp_admin_token"
    test_event = {
        "authorizationToken": auth_token,
        "methodArn": f"{MOCK_METHOD_ARN_PREFIX}/GET/SearchDocumentReferences",
    }

    response = lambda_handler(event=test_event, context=context)

    mock_jwt_decode.assert_called_with(
        auth_token, TEST_PUBLIC_KEY, algorithms=["RS256"]
    )
    assert response["policyDocument"] == expected_allow_policy


def test_valid_pcse_token_return_allow_policy(
    mock_ssm, mock_session_table, mock_jwt_decode, context
):
    expected_allow_policy = {
        "Statement": [
            {
                "Action": "execute-api:Invoke",
                "Effect": "Allow",
                "Resource": [f"{MOCK_METHOD_ARN_PREFIX}/GET/SearchPatient"],
            }
        ],
        "Version": "2012-10-17",
    }

    test_event = {
        "authorizationToken": "valid_pcse_token",
        "methodArn": f"{MOCK_METHOD_ARN_PREFIX}/GET/SearchPatient",
    }

    response = lambda_handler(test_event, context=context)

    mock_jwt_decode.assert_called_with(
        "valid_pcse_token", TEST_PUBLIC_KEY, algorithms=["RS256"]
    )
    assert response["policyDocument"] == expected_allow_policy


def test_return_deny_policy_when_no_session_found(
    mock_ssm, mock_session_table, mock_jwt_decode, context
):
    mock_session_table.query.return_value = {"Count": 0, "Items": []}

    test_event = {
        "authorizationToken": "valid_pcse_token",
        "methodArn": f"{MOCK_METHOD_ARN_PREFIX}/GET/SearchPatient",
    }

    response = lambda_handler(test_event, context=context)

    assert response["policyDocument"] == DENY_ALL_POLICY


############### GP Clinical user allow/deny ###############


def test_validate_access_policy_returns_true_for_gp_clinical_on_document_delete():
    expected = True
    actual = validate_access_policy(
        "mock_verb", "/DocumentDelete", RepositoryRole.GP_CLINICAL.value
    )
    assert expected == actual


def test_validate_access_policy_returns_true_for_gp_clinical_on_document_manifest():
    expected = True
    actual = validate_access_policy(
        "mock_verb", "/DocumentManifest", RepositoryRole.GP_CLINICAL.value
    )
    assert expected == actual


def test_validate_access_policy_returns_true_for_gp_clinical_on_document_reference():
    expected = True
    actual = validate_access_policy(
        "mock_verb", "/DocumentReference", RepositoryRole.GP_CLINICAL.value
    )
    assert expected == actual


############### PCSE user allow/deny ###############


def test_validate_access_policy_returns_false_for_pcse_on_document_delete():
    expected = False
    actual = validate_access_policy(
        "mock_verb", "/DocumentDelete", RepositoryRole.PCSE.value
    )
    assert expected == actual


def test_validate_access_policy_returns_false_for_pcse_on_document_manifest():
    expected = False
    actual = validate_access_policy(
        "mock_verb", "/DocumentManifest", RepositoryRole.PCSE.value
    )
    assert expected == actual


def test_validate_access_policy_returns_false_for_pcse_on_document_reference():
    expected = False
    actual = validate_access_policy(
        "mock_verb", "/DocumentReference", RepositoryRole.PCSE.value
    )
    assert expected == actual


############### Unhappy paths ###############


def test_validate_access_policy_returns_false_for_unrecognised_path():
    expected = False
    actual = validate_access_policy(
        "mock_verb", "not_a_reconised_path", RepositoryRole.PCSE.value
    )
    assert expected == actual


def test_return_deny_policy_when_user_session_is_expired(
    mock_ssm, mock_session_table, mock_jwt_decode, context
):
    one_minute_ago = time.time() - 60
    expired_session = {
        "Count": 1,
        "Items": [
            {
                "NDRSessionId": "test_session_id",
                "sid": "test_cis2_session_id",
                "Subject": "test_cis2_user_id",
                "TimeToExist": one_minute_ago,
            }
        ],
    }
    mock_session_table.query.return_value = expired_session

    test_event = {
        "authorizationToken": "valid_pcse_token",
        "methodArn": f"{MOCK_METHOD_ARN_PREFIX}/GET/SearchPatient",
    }

    response = lambda_handler(test_event, context=context)

    assert response["policyDocument"] == DENY_ALL_POLICY


def test_invalid_token_return_deny_policy(
    mocker, mock_ssm, mock_session_table, context
):
    decode_mock = mocker.patch(
        "jwt.decode", side_effect=jwt.exceptions.InvalidTokenError
    )

    test_event = {
        "authorizationToken": "invalid_token",
        "methodArn": f"{MOCK_METHOD_ARN_PREFIX}/GET/SearchPatient",
    }
    response = lambda_handler(test_event, context=context)

    decode_mock.assert_called_with(
        "invalid_token", TEST_PUBLIC_KEY, algorithms=["RS256"]
    )
    assert response["policyDocument"] == DENY_ALL_POLICY


def test_invalid_signature_return_deny_policy(
    mocker, mock_ssm, mock_session_table, context
):
    decode_mock = mocker.patch(
        "jwt.decode", side_effect=jwt.exceptions.InvalidSignatureError
    )

    test_event = {
        "authorizationToken": "token_with_invalid_signature",
        "methodArn": f"{MOCK_METHOD_ARN_PREFIX}/GET/SearchPatient",
    }
    response = lambda_handler(test_event, context=context)

    decode_mock.assert_called_with(
        "token_with_invalid_signature", TEST_PUBLIC_KEY, algorithms=["RS256"]
    )

    assert response["policyDocument"] == DENY_ALL_POLICY
