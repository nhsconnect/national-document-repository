from dataclasses import dataclass
from unittest.mock import patch

import boto3
import jwt
import pytest
from handlers.authoriser_handler import lambda_handler
from moto import mock_ssm

MOCK_METHOD_ARN_PREFIX = "arn:aws:execute-api:eu-west-2:fake_arn:fake_api_endpoint/dev"
TEST_PUBLIC_KEY = "test_public_key"
TEST_PUBLIC_KEY_SSM_PARAM_NAME = "jwt_token_public_key"


@pytest.fixture
def context():
    @dataclass
    class LambdaContext:
        pass

    return LambdaContext()


@pytest.fixture()
def mock_ssm_public_key():
    with patch.dict(
        "os.environ", {"SSM_PARAM_JWT_TOKEN_PUBLIC_KEY": TEST_PUBLIC_KEY_SSM_PARAM_NAME}
    ):
        with mock_ssm():
            ssm = boto3.client("ssm", region_name="eu-west-2")
            ssm.put_parameter(
                Name=TEST_PUBLIC_KEY_SSM_PARAM_NAME,
                Value=TEST_PUBLIC_KEY,
                Type="SecureString",
            )
            yield


def test_valid_gp_token_return_allow_policy(mocker, mock_ssm_public_key, context):
    decoded_token = {"user_role": "GP"}
    decode_mock = mocker.patch("jwt.decode", return_value=decoded_token)
    expected_allow_policy = {
        "Statement": [
            {
                "Action": "execute-api:Invoke",
                "Effect": "Allow",
                "Resource": [f"{MOCK_METHOD_ARN_PREFIX}/*/*"],
            }
        ],
        "Version": "2012-10-17",
    }

    test_event = {
        "authorizationToken": "valid_gp_token",
        "methodArn": f"{MOCK_METHOD_ARN_PREFIX}/GET/SearchPatient",
    }

    response = lambda_handler(test_event, context)

    decode_mock.assert_called_with(
        "valid_gp_token", TEST_PUBLIC_KEY, algorithms=["RS256"]
    )
    assert response["policyDocument"] == expected_allow_policy


def test_valid_pcse_token_return_allow_policy(mocker, mock_ssm_public_key, context):
    decoded_token = {"user_role": "PCSE"}
    decode_mock = mocker.patch("jwt.decode", return_value=decoded_token)
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

    test_event = {
        "authorizationToken": "valid_pcse_token",
        "methodArn": f"{MOCK_METHOD_ARN_PREFIX}/GET/SearchPatient",
    }

    response = lambda_handler(test_event, context)

    decode_mock.assert_called_with(
        "valid_pcse_token", TEST_PUBLIC_KEY, algorithms=["RS256"]
    )
    assert response["policyDocument"] == expected_allow_policy


def test_invalid_token_return_deny_policy(mocker, mock_ssm_public_key, context):
    decode_mock = mocker.patch(
        "jwt.decode", side_effect=jwt.exceptions.InvalidTokenError
    )

    expected_deny_policy = {
        "Statement": [
            {
                "Action": "execute-api:Invoke",
                "Effect": "Deny",
                "Resource": [f"{MOCK_METHOD_ARN_PREFIX}/*/*"],
            }
        ],
        "Version": "2012-10-17",
    }

    test_event = {
        "authorizationToken": "invalid_token",
        "methodArn": f"{MOCK_METHOD_ARN_PREFIX}/GET/SearchPatient",
    }
    response = lambda_handler(test_event, context)

    decode_mock.assert_called_with(
        "invalid_token", TEST_PUBLIC_KEY, algorithms=["RS256"]
    )
    assert response["policyDocument"] == expected_deny_policy


def test_invalid_signature_return_deny_policy(mocker, mock_ssm_public_key, context):
    decode_mock = mocker.patch(
        "jwt.decode", side_effect=jwt.exceptions.InvalidSignatureError
    )

    expected_deny_policy = {
        "Statement": [
            {
                "Action": "execute-api:Invoke",
                "Effect": "Deny",
                "Resource": [f"{MOCK_METHOD_ARN_PREFIX}/*/*"],
            }
        ],
        "Version": "2012-10-17",
    }

    test_event = {
        "authorizationToken": "token_with_invalid_signature",
        "methodArn": f"{MOCK_METHOD_ARN_PREFIX}/GET/SearchPatient",
    }
    response = lambda_handler(test_event, context)

    decode_mock.assert_called_with(
        "token_with_invalid_signature", TEST_PUBLIC_KEY, algorithms=["RS256"]
    )

    assert response["policyDocument"] == expected_deny_policy
