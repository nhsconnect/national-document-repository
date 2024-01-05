from datetime import datetime

import pytest
from services.token_handler_ssm_service import TokenHandlerSSMService

MOCK_ROLE_CODE_RESPONSE = {
    "Parameters": [
        {
            "Name": "ods_code_pcse",
            "Type": "String",
            "Value": "X0123",
            "Version": 123,
            "Selector": "string",
            "SourceResult": "string",
            "LastModifiedDate": datetime(2015, 1, 1),
            "ARN": "string",
            "DataType": "string",
        },
        {
            "Name": "/auth/smartcard/role/gp_admin_multiple",
            "Type": "StringList",
            "Value": "R0001,R0002,R0003",
            "Version": 123,
            "Selector": "string",
            "SourceResult": "string",
            "LastModifiedDate": datetime(2015, 1, 1),
            "ARN": "string",
            "DataType": "string",
        },
        {
            "Name": "/auth/smartcard/role/gp_clinical",
            "Type": "String",
            "Value": "R0002",
            "Version": 123,
            "Selector": "string",
            "SourceResult": "string",
            "LastModifiedDate": datetime(2015, 1, 1),
            "ARN": "string",
            "DataType": "string",
        },
        {
            "Name": "/auth/smartcard/role/pcse",
            "Type": "String",
            "Value": "R0003",
            "Version": 123,
            "Selector": "string",
            "SourceResult": "string",
            "LastModifiedDate": datetime(2015, 1, 1),
            "ARN": "string",
            "DataType": "string",
        },
    ],
}

MOCK_JWT_PK_RESPONSE = {
    "Parameter": {
        "Name": "jwt_token_private_key",
        "Type": "SecureString",
        "Value": "jwt-private-key",
        "Version": 123,
        "Selector": "string",
        "SourceResult": "string",
        "LastModifiedDate": datetime(2015, 1, 1),
        "ARN": "string",
        "DataType": "string",
    }
}


@pytest.fixture
def mock_service(mocker):
    mocker.patch("boto3.client")
    service = TokenHandlerSSMService()
    yield service


@pytest.fixture
def mock_ssm(mocker, mock_service):
    client = mock_service.client
    mocker.patch.object(client, "get_parameter")
    mocker.patch.object(client, "get_parameters")
    yield client


def test_get_jwt_token(mock_service, mock_ssm):
    mock_ssm.get_parameter.return_value = MOCK_JWT_PK_RESPONSE
    actual = mock_service.get_jwt_private_key()

    mock_ssm.get_parameter.assert_called_once_with(
        Name="jwt_token_private_key", WithDecryption=True
    )
    assert actual == "jwt-private-key"


def test_get_ssm_parameters(mock_service, mock_ssm):
    mock_ssm.get_parameters.return_value = MOCK_ROLE_CODE_RESPONSE
    expected = ["R0001,R0002,R0003", "R0002", "R0003"]

    actual = mock_service.get_smartcard_role_codes()

    mock_ssm.get_parameters.assert_called_once_with(
        Names=[
            "/auth/smartcard/role/gp_admin_multiple",
            "/auth/smartcard/role/gp_clinical",
            "/auth/smartcard/role/pcse",
        ],
        WithDecryption=False,
    )
    assert actual == expected


def test_get_smartcard_role_gp_admin(mock_service, mock_ssm):
    mock_ssm.get_parameters.return_value = MOCK_ROLE_CODE_RESPONSE
    expected = ["R0001", "R0002", "R0003"]

    actual = mock_service.get_smartcard_role_gp_admin()

    mock_ssm.get_parameters.assert_called_once_with(
        Names=["/auth/smartcard/role/gp_admin_multiple"], WithDecryption=False
    )

    assert actual == expected
