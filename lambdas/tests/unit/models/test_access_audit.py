from freezegun import freeze_time
from models.access_audit import AccessAuditReason


@freeze_time("2024-01-01 12:00:00")
def test_access_audit_reason_creation():
    reason = AccessAuditReason(
        nhs_number="nhs_number",
        request_type="0",
        user_session_id="session123",
        user_id="user456",
        user_ods_code="ods789",
        reason_codes=["01", "02"],
        custom_reason="User requested access",
    )

    assert reason.type == "LloydGeorge#nhs_number#DECE"
    assert reason.user_session_id == "session123"
    assert reason.user_id == "user456"
    assert reason.user_ods_code == "ods789"
    assert reason.reason_codes == {
        "Coroner or medical examiner request",
        "Legal or insurance request",
    }
    assert reason.custom_reason == "User requested access"
    assert isinstance(reason.timestamp, int)
    assert reason.timestamp == 1704110400


def test_access_audit_reason_id_computed_field():
    reason = AccessAuditReason(
        nhs_number="nhs_number",
        request_type="0",
        user_session_id="session123",
        user_id="user456",
        user_ods_code="ods789",
        reason_codes={"01", "02"},
    )

    expected_id = f"{reason.user_session_id}#{reason.timestamp}"
    assert reason.id == expected_id


def test_access_audit_reason_alias_generation():
    reason = AccessAuditReason(
        nhs_number="nhs_number",
        request_type="0",
        user_session_id="session123",
        user_id="user456",
        user_ods_code="ods789",
        reason_codes={"01", "02"},
    )

    assert reason.model_dump(by_alias=True).get("ID") == reason.id
