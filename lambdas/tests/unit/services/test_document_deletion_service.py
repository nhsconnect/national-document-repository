import pytest
from enums.s3_lifecycle_tags import S3LifecycleTags
from enums.supported_document_types import SupportedDocumentTypes
from services.document_deletion_service import DocumentDeletionService
from tests.unit.conftest import (MOCK_ARF_TABLE_NAME, MOCK_LG_TABLE_NAME,
                                 TEST_NHS_NUMBER)
from tests.unit.helpers.data.test_documents import (
    create_test_doc_store_refs, create_test_lloyd_george_doc_store_refs)

TEST_DOC_STORE_REFERENCES = create_test_doc_store_refs()
TEST_LG_DOC_STORE_REFERENCES = create_test_lloyd_george_doc_store_refs()
TEST_NHS_NUMBER_WITH_NO_RECORD = "1234567890"


def mocked_document_query(nhs_number: str, doc_type: str):
    if nhs_number == TEST_NHS_NUMBER and doc_type == SupportedDocumentTypes.LG.value:
        return TEST_LG_DOC_STORE_REFERENCES
    elif nhs_number == TEST_NHS_NUMBER and doc_type == SupportedDocumentTypes.ARF.value:
        return TEST_DOC_STORE_REFERENCES
    return []


@pytest.fixture
def mock_delete_specific_doc_type(mocker):
    def mocked_method(nhs_number: str, doc_type: SupportedDocumentTypes):
        return mocked_document_query(nhs_number, doc_type.value)

    yield mocker.patch.object(
        DocumentDeletionService,
        "delete_specific_doc_type",
        side_effect=mocked_method,
    )


@pytest.fixture
def mock_document_query(mocker):
    yield mocker.patch(
        "services.document_service.DocumentService.fetch_available_document_references_by_type",
        side_effect=mocked_document_query,
    )


# @pytest.mark.parametrize(
#     ["nhs_number", "doc_type", "expected"],
#     [
#         (
#             TEST_NHS_NUMBER,
#             SupportedDocumentTypes.ALL,
#             TEST_DOC_STORE_REFERENCES + TEST_LG_DOC_STORE_REFERENCES,
#         ),
#         (TEST_NHS_NUMBER, SupportedDocumentTypes.ARF, TEST_DOC_STORE_REFERENCES),
#         (TEST_NHS_NUMBER, SupportedDocumentTypes.LG, TEST_LG_DOC_STORE_REFERENCES),
#     ],
# )
def test_handle_delete_for_all_doc_type(set_env, mock_delete_specific_doc_type):
    service = DocumentDeletionService()

    expected = TEST_DOC_STORE_REFERENCES + TEST_LG_DOC_STORE_REFERENCES

    actual = service.handle_delete(TEST_NHS_NUMBER, SupportedDocumentTypes.ALL)

    assert expected == actual

    assert mock_delete_specific_doc_type.call_count == 2
    mock_delete_specific_doc_type.assert_any_call(
        TEST_NHS_NUMBER, SupportedDocumentTypes.ARF
    )
    mock_delete_specific_doc_type.assert_any_call(
        TEST_NHS_NUMBER, SupportedDocumentTypes.LG
    )


@pytest.mark.parametrize(
    ["doc_type", "expected"],
    [
        (SupportedDocumentTypes.ARF, TEST_DOC_STORE_REFERENCES),
        (SupportedDocumentTypes.LG, TEST_LG_DOC_STORE_REFERENCES),
    ],
)
def test_handle_delete_for_one_doc_type(
    set_env, doc_type, expected, mock_delete_specific_doc_type
):
    service = DocumentDeletionService()

    actual = service.handle_delete(TEST_NHS_NUMBER, doc_type)

    assert actual == expected

    assert mock_delete_specific_doc_type.call_count == 1
    mock_delete_specific_doc_type.assert_called_with(TEST_NHS_NUMBER, doc_type)


def test_handle_delete_when_no_record_for_patient_return_empty_list(
    set_env,
    mock_delete_specific_doc_type,
):
    service = DocumentDeletionService()
    # mocker.patch("services.document_service.DocumentService.delete_documents")

    expected = []
    actual = service.handle_delete(
        TEST_NHS_NUMBER_WITH_NO_RECORD, SupportedDocumentTypes.ALL
    )

    assert actual == expected


@pytest.mark.parametrize(
    ["doc_type", "table_name", "doc_ref"],
    [
        (SupportedDocumentTypes.ARF, MOCK_ARF_TABLE_NAME, TEST_DOC_STORE_REFERENCES),
        (SupportedDocumentTypes.LG, MOCK_LG_TABLE_NAME, TEST_LG_DOC_STORE_REFERENCES),
    ],
)
def test_delete_specific_doc_type(
    set_env, doc_type, table_name, doc_ref, mocker, mock_document_query
):
    service = DocumentDeletionService()
    mock_delete_doc = mocker.patch(
        "services.document_service.DocumentService.delete_documents"
    )
    type_of_delete = str(S3LifecycleTags.SOFT_DELETE.value)

    expected = doc_ref
    actual = service.delete_specific_doc_type(TEST_NHS_NUMBER, doc_type)

    assert actual == expected

    mock_delete_doc.assert_called_once_with(
        table_name=table_name,
        document_references=doc_ref,
        type_of_delete=type_of_delete,
    )


@pytest.mark.parametrize(
    "doc_type",
    [SupportedDocumentTypes.ARF, SupportedDocumentTypes.LG],
)
def test_delete_specific_doc_type_when_no_record_for_given_patient(
    set_env, doc_type, mocker, mock_document_query
):
    service = DocumentDeletionService()
    mock_delete_doc = mocker.patch(
        "services.document_service.DocumentService.delete_documents"
    )

    expected = []
    actual = service.delete_specific_doc_type(TEST_NHS_NUMBER_WITH_NO_RECORD, doc_type)

    assert actual == expected

    mock_delete_doc.assert_not_called()
