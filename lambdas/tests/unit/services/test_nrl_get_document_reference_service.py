import pytest
from enums.patient_ods_inactive_status import PatientOdsInactiveStatus
from services.nrl_get_document_reference_service import NRLGetDocumentReferenceService
from tests.unit.conftest import FAKE_URL, TEST_CURRENT_GP_ODS, TEST_UUID
from tests.unit.helpers.data.test_documents import create_test_doc_store_refs
from utils.lambda_exceptions import NRLGetDocumentReferenceException

MOCK_USER_INFO = {
    "nhsid_useruid": TEST_UUID,
    "name": "TestUserOne Caius Mr",
    "nhsid_nrbac_roles": [
        {
            "person_orgid": "500000000000",
            "person_roleid": TEST_UUID,
            "org_code": "B9A5A",
            "role_name": '"Support":"Systems Support":"Systems Support Access Role"',
            "role_code": "S8001:G8005:R8000",
        },
        {
            "person_orgid": "500000000000",
            "person_roleid": "500000000000",
            "org_code": "B9A5A",
            "role_name": '"Primary Care Support England":"Systems Support Access Role"',
            "role_code": "S8001:G8005:R8015",
        },
        {
            "person_orgid": "500000000000",
            "person_roleid": "500000000000",
            "org_code": TEST_CURRENT_GP_ODS,
            "role_name": '"Primary Care Support England":"Systems Support Access Role"',
            "role_code": "S8001:G8005:R8008",
        },
    ],
    "given_name": "Caius",
    "family_name": "TestUserOne",
    "uid": "500000000000",
    "nhsid_user_orgs": [
        {"org_name": "NHSID DEV", "org_code": "A9A5A"},
        {"org_name": "Primary Care Support England", "org_code": "B9A5A"},
    ],
    "sub": "500000000000",
}


@pytest.fixture
def patched_service(mocker, set_env, context):
    mocker.patch("services.base.s3_service.IAMService")

    service = NRLGetDocumentReferenceService()
    mocker.patch.object(service, "ssm_service")
    mocker.patch.object(service, "s3_service")
    mocker.patch.object(service, "pds_service")
    mocker.patch.object(service, "document_service")
    mocker.patch.object(service, "get_ndr_accepted_role_codes")
    yield service


@pytest.fixture
def mock_fetch_user_info(patched_service, mocker):
    service = patched_service
    mocker.patch.object(service, "get_user_roles_and_ods_codes")
    mocker.patch.object(service, "fetch_user_info")
    mocker.patch.object(service, "get_patient_current_gp_ods")
    mocker.patch.object(service, "patient_is_inactive")
    yield service


@pytest.mark.parametrize(
    "input, expected",
    [
        ("S8001:G8005:R8000", "R8000"),
        ("S8001:G8005:R8015", "R8015"),
        ("S8001:G8005:R8008", "R8008"),
    ],
)
def test_process_role_code_returns_correct_role(patched_service, input, expected):
    assert patched_service.process_role_code(input) == expected


def test_get_user_roles_and_ods_codes(patched_service):
    expected = {"B9A5A": ["R8000", "R8015"], TEST_CURRENT_GP_ODS: ["R8008"]}

    assert patched_service.get_user_roles_and_ods_codes(MOCK_USER_INFO) == expected


def test_get_document_reference_service(patched_service):
    (patched_service.document_service.fetch_documents_from_table.return_value) = (
        create_test_doc_store_refs()
    )

    actual = patched_service.get_document_references(
        "3d8683b9-1665-40d2-8499-6e8302d507ff"
    )
    assert actual == create_test_doc_store_refs()[0]


def test_handle_get_document_reference_request(patched_service, mocker):
    expected = "test_response"
    mock_document_ref = create_test_doc_store_refs()[0]
    mocker.patch.object(
        patched_service, "get_document_references", return_value=mock_document_ref
    )
    mocker.patch.object(patched_service, "fetch_user_info", return_value=MOCK_USER_INFO)
    mocker.patch.object(
        patched_service, "is_user_allowed_to_see_file", return_value=True
    )
    mocker.patch.object(
        patched_service, "create_document_presigned_url", return_value=FAKE_URL
    )
    mocker.patch.object(
        patched_service,
        "create_document_reference_fhir_response",
        return_value=expected,
    )

    actual = patched_service.handle_get_document_reference_request(
        "test-id", "bearer token_test"
    )

    assert expected == actual
    patched_service.create_document_reference_fhir_response.assert_called_once_with(
        mock_document_ref, FAKE_URL
    )


def test_handle_get_document_reference_request_when_user_is_not_allowed_access(
    patched_service, mocker
):
    mock_document_ref = create_test_doc_store_refs()[0]
    mocker.patch.object(
        patched_service, "get_document_references", return_value=mock_document_ref
    )
    mocker.patch.object(patched_service, "fetch_user_info", return_value=MOCK_USER_INFO)
    mocker.patch.object(
        patched_service, "is_user_allowed_to_see_file", return_value=False
    )
    mocker.patch.object(
        patched_service, "create_document_presigned_url", return_value=FAKE_URL
    )
    mocker.patch.object(patched_service, "create_document_reference_fhir_response")

    with pytest.raises(NRLGetDocumentReferenceException):
        patched_service.handle_get_document_reference_request(
            "test-id", "bearer token_test"
        )

    patched_service.create_document_reference_fhir_response.assert_not_called()


def test_create_document_reference_fhir_response(patched_service):
    actual = patched_service.create_document_reference_fhir_response(
        create_test_doc_store_refs()[0], FAKE_URL
    )
    assert actual["content"][0]["attachment"]["url"] == FAKE_URL


def test_user_allowed_to_see_file_happy_path(patched_service, mock_fetch_user_info):
    patched_service.get_user_roles_and_ods_codes.return_value = {
        "TEST_ODS": ["R8000", "R3002", "R8003"],
        "Y12345": ["R8000", "R1234"],
    }

    patched_service.get_ndr_accepted_role_codes.return_value = ["R8000", "R8008"]
    patched_service.get_patient_current_gp_ods.return_value = TEST_CURRENT_GP_ODS
    patched_service.patient_is_inactive.return_value = False

    assert (
        patched_service.is_user_allowed_to_see_file(
            TEST_UUID, create_test_doc_store_refs()[0]
        )
        is True
    )


def test_user_allowed_to_see_file_returns_false(patched_service, mock_fetch_user_info):
    patched_service.get_user_roles_and_ods_codes.return_value = {
        "TEST_ODS": ["R8001", "R3002", "R8003"],
        "Y12345": ["R8001", "R1234"],
    }

    patched_service.get_ndr_accepted_role_codes.return_value = ["R8000", "R8008"]
    patched_service.get_patient_current_gp_ods.return_value = TEST_CURRENT_GP_ODS
    patched_service.patient_is_inactive.return_value = False

    assert (
        patched_service.is_user_allowed_to_see_file(
            TEST_UUID, create_test_doc_store_refs()[0]
        )
        is False
    )


def test_user_allowed_to_see_file_inactive_patient(
    patched_service, mock_fetch_user_info
):
    patched_service.get_user_roles_and_ods_codes.return_value = {
        "TEST_ODS": ["R8000", "R3002", "R8003"],
        "Y12345": ["R8000", "R1234"],
    }

    patched_service.get_ndr_accepted_role_codes.return_value = ["R8000", "R8008"]
    patched_service.get_patient_current_gp_ods.return_value = (
        PatientOdsInactiveStatus.DECEASED
    )
    patched_service.patient_is_inactive.return_value = True

    assert (
        patched_service.is_user_allowed_to_see_file(
            TEST_UUID, create_test_doc_store_refs()[0]
        )
        is False
    )
