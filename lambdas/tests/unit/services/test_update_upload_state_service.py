import pytest
from services.update_upload_state_service import UpdateUploadStateService
from tests.unit.helpers.data.update_upload_state import (
    MOCK_ARF_DOCTYPE,
    MOCK_ARF_DOCUMENT_REFERENCE,
    MOCK_ARF_DOCUMENTS_REQUEST,
    MOCK_LG_DOCTYPE,
    MOCK_LG_DOCUMENT_REFERENCE,
    MOCK_LG_DOCUMENTS_REQUEST,
)


@pytest.fixture
def patched_service(set_env, mocker):
    service = UpdateUploadStateService()
    mock_dynamo_service = mocker.patch.object(service, "dynamo_service")
    mocker.patch.object(mock_dynamo_service, "update_item")
    yield service


@pytest.fixture
def mock_update_document(patched_service, mocker):
    yield mocker.patch.object(patched_service, "update_document")


@pytest.fixture
def mock_format_update(patched_service, mocker):
    yield mocker.patch.object(patched_service, "format_update")


def test_process_documents_with_lg_document_references(
    patched_service,
    mock_update_document,
):
    patched_service.handle_update_state(MOCK_LG_DOCUMENTS_REQUEST)

    mock_update_document.assert_called_with(
        MOCK_LG_DOCUMENT_REFERENCE, MOCK_LG_DOCTYPE, "true"
    )


def test_process_documents_with_arf_document_references(
    patched_service,
    mock_update_document,
):
    patched_service.handle_update_state(MOCK_ARF_DOCUMENTS_REQUEST)

    mock_update_document.assert_called_with(
        MOCK_ARF_DOCUMENT_REFERENCE, MOCK_ARF_DOCTYPE, "true"
    )


# def test_process_documents_with_both_types_of_document_references(
#     patched_service,
#     mock_validate_number_of_documents,
#     mock_move_files_and_update_dynamo,
# ):
#     patched_service.process_documents(MOCK_BOTH_DOC_TYPES)

#     mock_validate_number_of_documents.assert_called_once_with(
#         SupportedDocumentTypes.LG, [TEST_FILE_KEY]
#     )
#     assert mock_move_files_and_update_dynamo.call_count == 2

# def test_process_documents_when_no_lg_or_arf_doc_type_in_documents_raises_exception(
#     patched_service,
#     mock_validate_number_of_documents,
#     mock_move_files_and_update_dynamo,
# ):
#     with pytest.raises(UploadConfirmResultException):
#         patched_service.process_documents(MOCK_NO_DOC_TYPE)

#     mock_validate_number_of_documents.assert_not_called()
#     mock_move_files_and_update_dynamo.assert_not_called()


# def test_process_documents_when_dynamo_throws_error(
#     patched_service, mock_update_dynamo_table
# ):
#     mock_update_dynamo_table.side_effect = ClientError(
#         {"Error": {"Code": "500", "Message": "test error"}}, "testing"
#     )

#     with pytest.raises(UploadConfirmResultException):
#         patched_service.process_documents(MOCK_ARF_DOCUMENTS)
