from datetime import datetime

import pytest
from enums.lambda_error import LambdaError
from services.token_handler_ssm_service import TokenHandlerSSMService
from utils.constants.ssm import (
    ALLOWED_ODS_CODES_LIST,
    GP_ADMIN_USER_ROLE_CODES,
    GP_CLINICAL_USER_ROLE_CODE,
    GP_ORG_ROLE_CODE,
    ITOC_ODS_CODES,
    PCSE_ODS_CODE,
    PCSE_USER_ROLE_CODE,
    ALLOWED_ODS_CODES_LIST_PILOT
)
from utils.lambda_exceptions import LoginException

MOCK_ROLE_CODE_RESPONSES = {
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
            "Value": "R0004,R0005,R0006",
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
            "Value": "R0007,R0008,R0009",
            "Version": 123,
            "Selector": "string",
            "SourceResult": "string",
            "LastModifiedDate": datetime(2015, 1, 1),
            "ARN": "string",
            "DataType": "string",
        },
    ],
}

MOCK_PCSE_ODS_CODE_RESPONSE = {
    "Parameter": {
        "Name": PCSE_ODS_CODE,
        "Type": "SecureString",
        "Value": "R0011",
        "Version": 123,
        "Selector": "string",
        "SourceResult": "string",
        "LastModifiedDate": datetime(2015, 1, 1),
        "ARN": "string",
        "DataType": "string",
    },
}

MOCK_ITOC_ODS_CODE_RESPONSE = {
    "Parameter": {
        "Name": ITOC_ODS_CODES,
        "Type": "SecureString",
        "Value": "R0012,R0120",
        "Version": 123,
        "Selector": "string",
        "SourceResult": "string",
        "LastModifiedDate": datetime(2015, 1, 1),
        "ARN": "string",
        "DataType": "string",
    },
}

MOCK_ALLOWED_LIST_OF_ODS_CODES = {
    "Parameter": {
        "Name": ALLOWED_ODS_CODES_LIST,
        "Type": "StringList",
        "Value": "R0013,R0014,R0015",
        "Version": 123,
        "Selector": "string",
        "SourceResult": "string",
        "LastModifiedDate": datetime(2015, 1, 1),
        "ARN": "string",
        "DataType": "string",
    },
}

MOCK_ALLOWED_ODS_CODES_LIST_PILOT = {
    "Parameter": {
        "Name": ALLOWED_ODS_CODES_LIST_PILOT,
        "Type": "StringList",
        "Value": "PI001,PI002,PI003",
        "Version": 123,
        "Selector": "string",
        "SourceResult": "string",
        "LastModifiedDate": datetime(2015, 1, 1),
        "ARN": "string",
        "DataType": "string",
    },
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
    mock_ssm.get_parameters.return_value = MOCK_ROLE_CODE_RESPONSES
    expected = ["R0001,R0002,R0003", "R0004,R0005,R0006", "R0007,R0008,R0009"]

    actual = mock_service.get_smartcard_role_codes()

    mock_ssm.get_parameters.assert_called_once_with(
        Names=[
            GP_ADMIN_USER_ROLE_CODES,
            GP_CLINICAL_USER_ROLE_CODE,
            PCSE_USER_ROLE_CODE,
        ],
        WithDecryption=False,
    )
    assert actual == expected


def test_get_smartcard_role_gp_admin(mock_service, mock_ssm):
    mock_ssm.get_parameters.return_value = MOCK_ROLE_CODE_RESPONSES
    expected = ["R0001", "R0002", "R0003"]

    actual = mock_service.get_smartcard_role_gp_admin()

    mock_ssm.get_parameters.assert_called_once_with(
        Names=[GP_ADMIN_USER_ROLE_CODES], WithDecryption=False
    )

    assert actual == expected


def test_get_smartcard_role_gp_admin_raises_login_exception(mock_service, mock_ssm):
    mock_ssm.get_parameters.return_value = {"Parameters": []}
    expected = LoginException(500, LambdaError.LoginAdminSSM)

    with pytest.raises(LoginException) as actual:
        mock_service.get_smartcard_role_gp_admin()

    mock_ssm.get_parameters.assert_called_once_with(
        Names=[GP_ADMIN_USER_ROLE_CODES], WithDecryption=False
    )

    assert actual.value.__dict__ == expected.__dict__


def test_get_smartcard_role_gp_clinical(mock_service, mock_ssm):
    mock_ssm.get_parameters.return_value = MOCK_ROLE_CODE_RESPONSES
    expected = ["R0004", "R0005", "R0006"]

    actual = mock_service.get_smartcard_role_gp_clinical()

    mock_ssm.get_parameters.assert_called_once_with(
        Names=[GP_CLINICAL_USER_ROLE_CODE], WithDecryption=False
    )

    assert actual == expected


def test_get_smartcard_role_gp_clinical_raises_login_exception(mock_service, mock_ssm):
    mock_ssm.get_parameters.return_value = {"Parameters": []}
    expected = LoginException(500, LambdaError.LoginClinicalSSM)

    with pytest.raises(LoginException) as actual:
        mock_service.get_smartcard_role_gp_clinical()

    mock_ssm.get_parameters.assert_called_once_with(
        Names=[GP_CLINICAL_USER_ROLE_CODE], WithDecryption=False
    )

    assert actual.value.__dict__ == expected.__dict__


def test_get_smartcard_role_pcse(mock_service, mock_ssm):
    mock_ssm.get_parameters.return_value = MOCK_ROLE_CODE_RESPONSES
    expected = ["R0007", "R0008", "R0009"]

    actual = mock_service.get_smartcard_role_pcse()

    mock_ssm.get_parameters.assert_called_once_with(
        Names=[PCSE_USER_ROLE_CODE], WithDecryption=False
    )

    assert actual == expected


def test_get_smartcard_role_pcse_raises_login_exception(mock_service, mock_ssm):
    mock_ssm.get_parameters.return_value = {"Parameters": []}
    expected = LoginException(500, LambdaError.LoginPcseSSM)

    with pytest.raises(LoginException) as actual:
        mock_service.get_smartcard_role_pcse()

    mock_ssm.get_parameters.assert_called_once_with(
        Names=[PCSE_USER_ROLE_CODE], WithDecryption=False
    )

    assert actual.value.__dict__ == expected.__dict__


def test_get_pcse_ods_code(mock_service, mock_ssm):
    mock_ssm.get_parameter.return_value = MOCK_PCSE_ODS_CODE_RESPONSE
    expected = "R0011"

    actual = mock_service.get_pcse_ods_code()

    mock_ssm.get_parameter.assert_called_once_with(
        Name=PCSE_ODS_CODE, WithDecryption=False
    )

    assert actual == expected


def test_get_pcse_ods_code_raises_login_exception(mock_service, mock_ssm):
    mock_ssm.get_parameter.return_value = {
        "Parameter": {"Value": ""},
    }
    expected = LoginException(500, LambdaError.LoginPcseOdsCode)

    with pytest.raises(LoginException) as actual:
        mock_service.get_pcse_ods_code()

    mock_ssm.get_parameter.assert_called_once_with(
        Name=PCSE_ODS_CODE, WithDecryption=False
    )

    assert actual.value.__dict__ == expected.__dict__


def test_get_itoc_ods_codes(mock_service, mock_ssm):
    mock_ssm.get_parameter.return_value = MOCK_ITOC_ODS_CODE_RESPONSE
    expected = ["R0012", "R0120"]

    actual = mock_service.get_itoc_ods_codes()

    mock_ssm.get_parameter.assert_called_once_with(
        Name=ITOC_ODS_CODES, WithDecryption=False
    )

    assert actual == expected


def test_get_itoc_ods_codes_raises_login_exception(mock_service, mock_ssm):
    mock_ssm.get_parameter.return_value = {
        "Parameter": {"Value": ""},
    }
    expected = LoginException(500, LambdaError.LoginItocOdsCodes)

    with pytest.raises(LoginException) as actual:
        mock_service.get_itoc_ods_codes()

    mock_ssm.get_parameter.assert_called_once_with(
        Name=ITOC_ODS_CODES, WithDecryption=False
    )

    assert actual.value.__dict__ == expected.__dict__


def test_get_allowed_list_of_ods_codes(mock_service, mock_ssm):
    mock_ssm.get_parameter.return_value = MOCK_ALLOWED_LIST_OF_ODS_CODES
    expected = "R0013,R0014,R0015"

    actual = mock_service.get_allowed_list_of_ods_codes()

    mock_ssm.get_parameter.assert_called_once_with(
        Name=ALLOWED_ODS_CODES_LIST, WithDecryption=False
    )

    assert actual == expected

def test_get_allowed_list_of_ods_codes_for_pilot(mock_service, mock_ssm):
    mock_ssm.get_parameter.return_value = MOCK_ALLOWED_ODS_CODES_LIST_PILOT
    expected = "PI001,PI002,PI003"

    actual = mock_service.get_allowed_list_of_ods_codes_for_pilot()

    mock_ssm.get_parameter.assert_called_once_with(
        Name=ALLOWED_ODS_CODES_LIST_PILOT, WithDecryption=False
    )

    assert actual == expected
