import pytest
from botocore.exceptions import ClientError
from services.update_upload_state_service import UpdateUploadStateService
from tests.unit.helpers.data.update_upload_state import (
    MOCK_ALL_DOCUMENTS_REQUEST,
    MOCK_ARF_DOCTYPE,
    MOCK_ARF_DOCUMENTS_REQUEST,
    MOCK_DOCUMENT_REFERENCE,
    MOCK_LG_DOCTYPE,
    MOCK_LG_DOCUMENTS_REQUEST,
    MOCK_NO_DOCTYPE_REQUEST,
    MOCK_NO_FIELDS_REQUEST,
    MOCK_NO_REFERENCE_REQUEST,
)
from utils.lambda_exceptions import UpdateUploadStateException


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
        MOCK_DOCUMENT_REFERENCE, MOCK_LG_DOCTYPE, "true"
    )


def test_process_documents_with_arf_document_references(
    patched_service, mock_update_document, mock_format_update
):
    patched_service.handle_update_state(MOCK_ARF_DOCUMENTS_REQUEST)

    mock_update_document.assert_called_with(
        MOCK_DOCUMENT_REFERENCE, MOCK_ARF_DOCTYPE, "true"
    )


def test_process_documents_when_doc_type_empty_and_raises_exception(
    patched_service,
    mock_update_document,
    mock_format_update,
):
    with pytest.raises(UpdateUploadStateException):
        patched_service.handle_update_state(MOCK_NO_DOCTYPE_REQUEST)

    mock_update_document.assert_not_called()
    mock_format_update.assert_not_called()


def test_process_documents_when_doc_ref_empty_and_raises_exception(
    patched_service,
    mock_update_document,
    mock_format_update,
):
    with pytest.raises(UpdateUploadStateException):
        patched_service.handle_update_state(MOCK_NO_REFERENCE_REQUEST)

    mock_update_document.assert_not_called()
    mock_format_update.assert_not_called()


def test_process_documents_when_fields_empty_and_raises_exception(
    patched_service,
    mock_update_document,
    mock_format_update,
):
    with pytest.raises(UpdateUploadStateException):
        patched_service.handle_update_state(MOCK_NO_FIELDS_REQUEST)

    mock_update_document.assert_not_called()
    mock_format_update.assert_not_called()


def test_process_documents_when_doctype_ALL_and_raises_exception(
    patched_service,
    mock_update_document,
    mock_format_update,
):
    with pytest.raises(UpdateUploadStateException):
        patched_service.handle_update_state(MOCK_ALL_DOCUMENTS_REQUEST)

    mock_update_document.assert_not_called()
    mock_format_update.assert_not_called()


def test_update_document_when_dynamo_throws_error(patched_service):
    patched_service.dynamo_service.update_item.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "test error"}}, "testing"
    )

    with pytest.raises(UpdateUploadStateException):
        patched_service.handle_update_state(MOCK_LG_DOCUMENTS_REQUEST)
