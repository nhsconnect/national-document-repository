from unittest.mock import patch
import pytest
import boto3
from moto import mock_ssm
from dataclasses import dataclass

from handlers.authoriser_handler import lambda_handler as auth_lambda

@pytest.fixture
def context():
    @dataclass
    class LambdaContext:
        pass
    return LambdaContext()

# def test_token():
#     private_key = b"testtsdfushd"
#     token = jwt.encode(test_json, private_key, algorithm="RS256")
#     event = {'authorizationToken': token}
#     auth_lambda.lambda_handler(event, context)

@mock_ssm
def test_valid_gp_token_return_allow_policy(context):
    with patch("handler.jwt.decode") as decode_mock:
        ssm = boto3.client('ssm')
        ssm.put_parameter(
            Name="jwt_token_public_key",
            Value="test_public_key",
            Type="SecureString",
        )
        event = {'authorizationToken': "valid_token"}
        decode_mock.return_value = {'user_role' : 'GP'}
        response = auth_lambda.lambda_handler(event, context)
        print(response)


def test_valid_pcse_token_return_allow_policy():
    pass

def test_invalid_token_return_deny_policy():
    pass

def test_invalid_signature_return_deny_policy():
    pass
