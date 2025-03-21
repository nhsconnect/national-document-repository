from enums.access_audit_request_type import AccessAuditRequestType


def test_access_audit_request_type_creation():
    assert AccessAuditRequestType.DECEASED_PATIENT.value == "0"
    assert AccessAuditRequestType.DECEASED_PATIENT.additional_value == "DECE"


def test_access_audit_request_type_list():
    assert AccessAuditRequestType.list() == ["0"]


def test_access_audit_request_type_enum_members():
    assert AccessAuditRequestType.DECEASED_PATIENT in AccessAuditRequestType
