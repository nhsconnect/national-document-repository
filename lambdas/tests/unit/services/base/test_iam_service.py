from datetime import datetime

import pytest
from botocore.exceptions import ClientError
from services.base.iam_service import IAMService


@pytest.fixture
def mock_service(mock_client, set_env):
    service = IAMService()
    yield service


@pytest.fixture()
def mock_client(mocker):
    client = mocker.patch("boto3.client")
    yield client


def test_assume_role(mock_client, mock_service):
    assume_role_arn = "arn:aws:tests"
    resource_name = "test_resource_name"
    mock_service.sts_client.assume_role.return_value = ASSUME_ROLE_RESPONSE

    mock_service.assume_role(
        assume_role_arn=assume_role_arn, resource_name=resource_name
    )

    mock_service.sts_client.assume_role.assert_called_once_with(
        RoleArn=assume_role_arn, RoleSessionName=resource_name + " tests"
    )
    mock_client.assert_called_with(
        resource_name,
        aws_access_key_id="AccessKeyIdstring",
        aws_secret_access_key="SecretAccessKeystring",
        aws_session_token="SessionTokenstring",
        config=None,
    )


def test_assume_role_raise_error(mock_client, mock_service):
    assume_role_arn = "arn:aws:tests"
    resource_name = "test_resource_name"
    mock_service.sts_client.assume_role.side_effect = ClientError(
        {
            "Error": {
                "Code": "test",
                "Message": "test",
            }
        },
        "test",
    )
    with pytest.raises(ClientError):
        mock_service.assume_role(
            assume_role_arn=assume_role_arn, resource_name=resource_name
        )

    mock_service.sts_client.assume_role.assert_called_once_with(
        RoleArn=assume_role_arn, RoleSessionName=resource_name + " tests"
    )


ASSUME_ROLE_RESPONSE = {
    "Credentials": {
        "AccessKeyId": "AccessKeyIdstring",
        "SecretAccessKey": "SecretAccessKeystring",
        "SessionToken": "SessionTokenstring",
        "Expiration": datetime(2015, 1, 1),
    },
    "AssumedRoleUser": {"AssumedRoleId": "AssumedRoleIdstring", "Arn": "string"},
    "PackedPolicySize": 123,
    "SourceIdentity": "string",
}
