import pytest
from enums.access_audit_request_type import AccessAuditRequestType
from enums.deceased_access_reason import DeceasedAccessReason
from enums.lambda_error import LambdaError
from models.access_audit import AccessAuditReason
from services.access_audit_service import AccessAuditService
from tests.unit.conftest import TEST_NHS_NUMBER, TEST_UUID
from utils.lambda_exceptions import AccessAuditException
from utils.request_context import request_context


@pytest.fixture
def mock_service(set_env, mocker):
    mocker.patch("os.getenv", return_value="access-audit-table")
    service = AccessAuditService()
    mocker.patch.object(service, "db_service")
    mocker.patch.object(service, "manage_user_session_service")
    return service


@pytest.fixture
def setup_request_context():
    request_context.authorization = {
        "ndr_session_id": TEST_UUID,
        "nhs_user_id": "test-user-id",
        "selected_organisation": {"org_ods_code": "test-ods-code"},
    }
    yield
    request_context.authorization = {}


def test_manage_access_request_calls_correct_methods(
    mock_service, setup_request_context, mocker
):
    nhs_number = TEST_NHS_NUMBER
    request_type = AccessAuditRequestType.DECEASED_PATIENT.value
    request = {"Reasons": [DeceasedAccessReason.MEDICAL.value]}

    mock_arrange = mocker.patch.object(
        mock_service, "arrange_access_request", return_value={"test": "data"}
    )
    mock_write = mocker.patch.object(mock_service, "write_to_access_audit_table")
    mock_update = mocker.patch.object(mock_service, "update_auth_session_table")

    mock_service.manage_access_request(nhs_number, request, request_type)

    mock_arrange.assert_called_once_with(nhs_number, request_type, request)
    mock_write.assert_called_once_with({"test": "data"})
    mock_update.assert_called_once_with(nhs_number)


def test_validate_request_valid_inputs(mock_service, setup_request_context):
    request_type = AccessAuditRequestType.DECEASED_PATIENT.value
    request = {"Reasons": [DeceasedAccessReason.MEDICAL.value]}
    nhs_number = TEST_NHS_NUMBER
    response = mock_service.arrange_access_request(nhs_number, request_type, request)

    assert response["ReasonCodes"] == {DeceasedAccessReason.MEDICAL.additional_value}
    assert response.get("CustomReason") is None
    assert response.get("RequestType") is None


def test_validate_request_with_other_reason(mock_service, setup_request_context):
    request_type = AccessAuditRequestType.DECEASED_PATIENT.value
    nhs_number = TEST_NHS_NUMBER

    request = {
        "Reasons": [DeceasedAccessReason.OTHER.value],
        "OtherReasonText": "Custom reason explanation",
    }

    response = mock_service.arrange_access_request(nhs_number, request_type, request)

    assert response["ReasonCodes"] == {DeceasedAccessReason.OTHER.additional_value}
    assert response.get("CustomReason") == "Custom reason explanation"


def test_validate_request_with_multiple_reasons(mock_service, setup_request_context):
    request_type = AccessAuditRequestType.DECEASED_PATIENT.value
    nhs_number = TEST_NHS_NUMBER

    request = {
        "Reasons": [
            DeceasedAccessReason.MEDICAL.value,
            DeceasedAccessReason.LEGAL.value,
        ]
    }

    response = mock_service.arrange_access_request(nhs_number, request_type, request)

    assert response["ReasonCodes"] == {
        DeceasedAccessReason.MEDICAL.additional_value,
        DeceasedAccessReason.LEGAL.additional_value,
    }
    assert response.get("CustomReason") is None


def test_validate_request_invalid_request_type(mock_service, setup_request_context):
    request_type = "INVALID_TYPE"
    request = {"Reasons": [DeceasedAccessReason.MEDICAL.value]}
    nhs_number = TEST_NHS_NUMBER

    with pytest.raises(AccessAuditException) as exc_info:
        mock_service.arrange_access_request(nhs_number, request_type, request)

    assert exc_info.value.status_code == 400
    assert exc_info.value.error == LambdaError.InvalidReasonInput


def test_validate_request_invalid_reason(mock_service, setup_request_context):
    request_type = AccessAuditRequestType.DECEASED_PATIENT.value
    request = {"Reasons": ["INVALID_REASON"]}
    nhs_number = TEST_NHS_NUMBER

    with pytest.raises(AccessAuditException) as exc_info:
        mock_service.arrange_access_request(nhs_number, request_type, request)

    assert exc_info.value.status_code == 400
    assert exc_info.value.error == LambdaError.InvalidReasonInput


def test_validate_request_no_reasons(mock_service, setup_request_context):
    request_type = AccessAuditRequestType.DECEASED_PATIENT.value
    request = {"Reasons": []}
    nhs_number = TEST_NHS_NUMBER

    with pytest.raises(AccessAuditException) as exc_info:
        mock_service.arrange_access_request(nhs_number, request_type, request)

    assert exc_info.value.status_code == 400
    assert exc_info.value.error == LambdaError.InvalidReasonInput


def test_validate_request_other_reason_without_text(
    mock_service, setup_request_context
):
    request_type = AccessAuditRequestType.DECEASED_PATIENT.value
    request = {"Reasons": [DeceasedAccessReason.OTHER.value], "OtherReasonText": ""}
    nhs_number = TEST_NHS_NUMBER

    with pytest.raises(AccessAuditException) as exc_info:
        mock_service.arrange_access_request(nhs_number, request_type, request)

    assert exc_info.value.status_code == 400
    assert exc_info.value.error == LambdaError.InvalidReasonInput


def test_validate_request_other_reason_text_too_long(
    mock_service, setup_request_context
):
    request_type = AccessAuditRequestType.DECEASED_PATIENT.value
    nhs_number = TEST_NHS_NUMBER

    request = {
        "Reasons": [DeceasedAccessReason.OTHER.value],
        "OtherReasonText": "x" * 10001,  # Exceeds 10000 character limit
    }

    with pytest.raises(AccessAuditException) as exc_info:
        mock_service.arrange_access_request(nhs_number, request_type, request)

    assert exc_info.value.status_code == 400
    assert exc_info.value.error == LambdaError.InvalidReasonInput


def test_arrange_access_request(mock_service, setup_request_context):
    nhs_number = TEST_NHS_NUMBER
    request_type = "0"
    request_example = {"Reasons": ["01", "02"]}

    result = mock_service.arrange_access_request(
        nhs_number, request_type, request_example
    )

    assert "Type" in result
    assert result["Type"] == f"LloydGeorge#{nhs_number}#DECE"
    assert "UserId" in result
    assert result["UserId"] == "test-user-id"
    assert "UserOdsCode" in result
    assert result["UserOdsCode"] == "test-ods-code"
    assert "UserSessionId" in result
    assert result["UserSessionId"] == TEST_UUID
    assert "Timestamp" in result
    assert "ReasonCodes" in result
    expected_codes = {
        DeceasedAccessReason.MEDICAL.additional_value,
        DeceasedAccessReason.LEGAL.additional_value,
    }
    assert set(result["ReasonCodes"]) == expected_codes
    assert "CustomReason" not in result


def test_arrange_access_request_with_custom_reason(mock_service, setup_request_context):
    nhs_number = TEST_NHS_NUMBER
    request_type = "0"
    request_example = {"Reasons": ["99"], "OtherReasonText": "Custom reason text"}

    result = mock_service.arrange_access_request(
        nhs_number, request_type, request_example
    )

    assert "Type" in result
    assert result["Type"] == f"LloydGeorge#{nhs_number}#DECE"
    assert "UserId" in result
    assert result["UserId"] == "test-user-id"
    assert "UserOdsCode" in result
    assert result["UserOdsCode"] == "test-ods-code"
    assert "UserSessionId" in result
    assert result["UserSessionId"] == TEST_UUID
    assert "Timestamp" in result
    assert "ReasonCodes" in result
    assert result["ReasonCodes"] == {DeceasedAccessReason.OTHER.additional_value}
    assert "CustomReason" in result
    assert result["CustomReason"] == "Custom reason text"


def test_sanitize_custom_reason():
    dangerous_input = """This has control chars \x00\x1F and 
    DynamoDB expression placeholders :param1 and #attribute1
    with $operators that might cause injection problems.
    """

    model = AccessAuditReason(
        nhs_number=TEST_NHS_NUMBER,
        request_type="0",
        user_session_id="test-session-id",
        user_id="test-user-id",
        user_ods_code="test-ods-code",
        reason_codes=["99"],
        custom_reason=dangerous_input,
    )

    sanitized = model.custom_reason
    assert "\x00" not in sanitized
    assert "\x1F" not in sanitized

    assert ":param1" not in sanitized
    assert "﹕param1" in sanitized  # With special colon

    assert "#attribute1" not in sanitized
    assert "＃attribute1" in sanitized  # With special hash

    # $ should be replaced
    assert "$operators" not in sanitized
    assert "＄operators" in sanitized  # With special dollar sign

    assert "This has control chars" in sanitized
    assert "that might cause injection problems" in sanitized


def test_write_to_access_audit_table(mock_service):
    audit_item = {"test": "data"}

    mock_service.write_to_access_audit_table(audit_item)

    mock_service.db_service.create_item.assert_called_once_with(
        table_name="access-audit-table", item=audit_item
    )


def test_update_auth_session_table(mock_service):
    nhs_number = TEST_NHS_NUMBER

    mock_service.update_auth_session_table(nhs_number)

    mock_service.manage_user_session_service.update_auth_session_with_permitted_search.assert_called_once_with(
        nhs_number=nhs_number, write_to_deceased_column=False
    )
