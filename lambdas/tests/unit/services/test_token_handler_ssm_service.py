from datetime import datetime

import pytest
from services.token_handler_ssm_service import TokenHandlerSSMService
from utils.constants.ssm import (
    GP_ADMIN_USER_ROLE_CODES,
    GP_CLINICAL_USER_ROLE_CODE,
    GP_ORG_ROLE_CODE,
    PCSE_ODS_CODE,
    PCSE_USER_ROLE_CODE,
)
from utils.lambda_exceptions import LoginException

MOCK_ROLE_CODE_RESPONSE = {
    "Parameters": [
        {
            "Name": GP_ORG_ROLE_CODE,
            "Type": "String",
            "Value": "G0123",
            "Version": 123,
            "Selector": "string",
            "SourceResult": "string",
            "LastModifiedDate": datetime(2015, 1, 1),
            "ARN": "string",
            "DataType": "string",
        },
        {
            "Name": PCSE_ODS_CODE,
            "Type": "String",
            "Value": "P0123",
            "Version": 123,
            "Selector": "string",
            "SourceResult": "string",
            "LastModifiedDate": datetime(2015, 1, 1),
            "ARN": "string",
            "DataType": "string",
        },
        {
            "Name": GP_ADMIN_USER_ROLE_CODES,
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
            "Name": GP_CLINICAL_USER_ROLE_CODE,
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
            "Name": PCSE_USER_ROLE_CODE,
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
            "/auth/smartcard/role/gp_admin",
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
        Names=["/auth/smartcard/role/gp_admin"], WithDecryption=False
    )

    assert actual == expected


def test_get_smartcard_role_gp_admin_raises_login_exception(mock_service, mock_ssm):
    mock_ssm.get_parameters.return_value = {"Parameters": []}
    expected = LoginException(
        500, "LIN_5006", "Failed to find SSM parameter value for user role"
    )

    with pytest.raises(LoginException) as actual:
        mock_service.get_smartcard_role_gp_admin()

    mock_ssm.get_parameters.assert_called_once_with(
        Names=["/auth/smartcard/role/gp_admin"], WithDecryption=False
    )

    assert actual.value.__dict__ == expected.__dict__


def test_get_smartcard_role_gp_clinical(mock_service, mock_ssm):
    mock_ssm.get_parameters.return_value = MOCK_ROLE_CODE_RESPONSE
    expected = "R0002"

    actual = mock_service.get_smartcard_role_gp_clinical()

    mock_ssm.get_parameters.assert_called_once_with(
        Names=["/auth/smartcard/role/gp_clinical"], WithDecryption=False
    )

    assert actual == expected


def test_get_smartcard_role_gp_clinical_raises_login_exception(mock_service, mock_ssm):
    mock_ssm.get_parameters.return_value = {"Parameters": []}
    expected = LoginException(
        500, "LIN_5007", "Failed to find SSM parameter value for user role"
    )

    with pytest.raises(LoginException) as actual:
        mock_service.get_smartcard_role_gp_clinical()

    mock_ssm.get_parameters.assert_called_once_with(
        Names=["/auth/smartcard/role/gp_clinical"], WithDecryption=False
    )

    assert actual.value.__dict__ == expected.__dict__


def test_get_smartcard_role_pcse(mock_service, mock_ssm):
    mock_ssm.get_parameters.return_value = MOCK_ROLE_CODE_RESPONSE
    expected = "R0003"

    actual = mock_service.get_smartcard_role_pcse()

    mock_ssm.get_parameters.assert_called_once_with(
        Names=["/auth/smartcard/role/pcse"], WithDecryption=False
    )

    assert actual == expected


def test_get_smartcard_role_pcse_raises_login_exception(mock_service, mock_ssm):
    mock_ssm.get_parameters.return_value = {"Parameters": []}
    expected = LoginException(
        500, "LIN_5008", "Failed to find SSM parameter value for user role"
    )

    with pytest.raises(LoginException) as actual:
        mock_service.get_smartcard_role_pcse()

    mock_ssm.get_parameters.assert_called_once_with(
        Names=["/auth/smartcard/role/pcse"], WithDecryption=False
    )

    assert actual.value.__dict__ == expected.__dict__


def test_get_org_role_codes(mock_service, mock_ssm):
    mock_ssm.get_parameters.return_value = MOCK_ROLE_CODE_RESPONSE
    expected = ["G0123"]

    actual = mock_service.get_org_role_codes()

    mock_ssm.get_parameters.assert_called_once_with(
        Names=["/auth/org/role_code/gpp"], WithDecryption=False
    )

    assert actual == expected


def test_get_org_role_codes_raises_login_exception(mock_service, mock_ssm):
    mock_ssm.get_parameters.return_value = {"Parameters": []}
    expected = LoginException(
        500, "LIN_5009", "Failed to find SSM parameter value for GP org role"
    )

    with pytest.raises(LoginException) as actual:
        mock_service.get_org_role_codes()

    mock_ssm.get_parameters.assert_called_once_with(
        Names=["/auth/org/role_code/gpp"], WithDecryption=False
    )

    assert actual.value.__dict__ == expected.__dict__


def test_get_org_ods_codes(mock_service, mock_ssm):
    mock_ssm.get_parameters.return_value = MOCK_ROLE_CODE_RESPONSE
    expected = ["P0123"]

    actual = mock_service.get_org_ods_codes()

    mock_ssm.get_parameters.assert_called_once_with(
        Names=["/auth/org/ods_code/pcse"], WithDecryption=False
    )

    assert actual == expected


def test_get_org_ods_codes_raises_login_exception(mock_service, mock_ssm):
    mock_ssm.get_parameters.return_value = {"Parameters": []}
    expected = LoginException(
        500, "LIN_5010", "SSM parameter values for PSCE ODS code may not exist"
    )

    with pytest.raises(LoginException) as actual:
        mock_service.get_org_ods_codes()

    mock_ssm.get_parameters.assert_called_once_with(
        Names=["/auth/org/ods_code/pcse"], WithDecryption=False
    )

    assert actual.value.__dict__ == expected.__dict__
