import pytest
from models.document_reference import DocumentReference
from services.nrl_get_document_reference_service import NRLGetDocumentReferenceService
from tests.unit.conftest import TEST_CURRENT_GP_ODS, TEST_UUID
from tests.unit.helpers.data.dynamo_responses import MOCK_SINGLE_DOCUMENT_RESPONSE

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
def mock_service(mocker, set_env, context):
    service = NRLGetDocumentReferenceService()
    mocker.patch.object(service, "ssm_service")
    mocker.patch.object(service, "pds_service")
    mocker.patch.object(service, "dynamo_service")
    mocker.patch.object(service, "get_ndr_accepted_role_codes")
    yield service


@pytest.fixture
def mock_fetch_user_info(mock_service, mocker):
    service = mock_service
    mocker.patch.object(service, "fetch_user_info")
    mocker.patch.object(service, "get_patient_current_gp_ods")
    yield service


@pytest.mark.parametrize(
    "input, expected",
    [
        ("S8001:G8005:R8000", "R8000"),
        ("S8001:G8005:R8015", "R8015"),
        ("S8001:G8005:R8008", "R8008"),
    ],
)
def test_process_role_code_returns_correct_role(mock_service, input, expected):
    assert mock_service.process_role_code(input) == expected


def test_get_user_roles_and_ods_codes(mock_service):
    expected = {"B9A5A": ["R8000", "R8015"], TEST_CURRENT_GP_ODS: ["R8008"]}

    assert mock_service.get_user_roles_and_ods_codes(MOCK_USER_INFO) == expected


def test_get_document_reference_service(mock_service):
    response = mock_service.dynamo_service.query_table_by_index.return_value = (
        MOCK_SINGLE_DOCUMENT_RESPONSE
    )
    expected = DocumentReference.model_validate(response["Items"][0])

    actual = mock_service.get_document_references(
        "3d8683b9-1665-40d2-8499-6e8302d507ff"
    )
    assert actual == expected


def test_user_allowed_to_see_file_happy_path(mock_service, mock_fetch_user_info):
    mock_fetch_user_info.fetch_user_info.return_value = MOCK_USER_INFO
    mock_service.dynamo_service.query_table_by_index.return_value = (
        MOCK_SINGLE_DOCUMENT_RESPONSE
    )
    mock_service.get_ndr_accepted_role_codes.return_value = ["R8000", "R8008"]
    mock_service.get_patient_current_gp_ods.return_value = TEST_CURRENT_GP_ODS
    assert (
        mock_service.user_allowed_to_see_file(
            TEST_UUID, "3d8683b9-1665-40d2-8499-6e8302d507ff"
        )
        is True
    )
