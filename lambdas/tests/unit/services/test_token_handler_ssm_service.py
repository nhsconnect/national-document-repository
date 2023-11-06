from datetime import datetime

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
            "Name": "/auth/smartcard/role/gp_admin",
            "Type": "String",
            "Value": "R0001",
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


def test_get_jwt_token(mocker):
    mocker.patch("boto3.client")
    service = TokenHandlerSSMService()
    mock_get_parameter = mocker.patch.object(service.client, "get_parameter")
    mock_get_parameter.return_value = MOCK_JWT_PK_RESPONSE
    actual = service.get_jwt_private_key()

    mock_get_parameter.assert_called_once_with(
        Name="jwt_token_private_key", WithDecryption=True
    )
    assert actual == "jwt-private-key"


def test_get_ssm_parameters(mocker):
    mocker.patch("boto3.client")
    service = TokenHandlerSSMService()
    mock_get_parameters = mocker.patch.object(service.client, "get_parameters")
    mock_get_parameters.return_value = MOCK_ROLE_CODE_RESPONSE
    expected = ["R0001", "R0002", "R0003"]

    actual = service.get_smartcard_role_codes()

    mock_get_parameters.assert_called_once_with(
        Names=["/auth/smartcard/role/gp_admin",
               "/auth/smartcard/role/gp_clinical",
               "/auth/smartcard/role/pcse"
               ], WithDecryption=False
    )
    assert actual == expected
