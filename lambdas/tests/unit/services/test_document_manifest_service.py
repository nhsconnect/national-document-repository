import os

import pytest
from enums.supported_document_types import SupportedDocumentTypes
from services.document_manifest_service import DocumentManifestService
from tests.unit.conftest import MOCK_BUCKET, TEST_NHS_NUMBER
from tests.unit.helpers.data.s3_responses import MOCK_PRESIGNED_URL_RESPONSE
from tests.unit.helpers.data.test_documents import (
    create_test_doc_store_refs, create_test_lloyd_george_doc_store_refs)
from utils.exceptions import DocumentManifestServiceException

TEST_DOC_STORE_DOCUMENT_REFS = create_test_doc_store_refs()
TEST_LLOYD_GEORGE_DOCUMENT_REFS = create_test_lloyd_george_doc_store_refs()


@pytest.fixture
def mock_service(mocker, set_env):
    service = DocumentManifestService(TEST_NHS_NUMBER)
    mocker.patch.object(service, "s3_service")
    mocker.patch.object(service, "dynamo_service")
    mocker.patch.object(service, "document_service")
    yield service


def test_create_document_manifest_presigned_url_doc_store(mock_service):
    mock_service.s3_service.create_download_presigned_url.return_value = (
        MOCK_PRESIGNED_URL_RESPONSE
    )
    mock_service.document_service.fetch_available_document_references_by_type.return_value = (
        TEST_DOC_STORE_DOCUMENT_REFS
    )

    response = mock_service.create_document_manifest_presigned_url(
        SupportedDocumentTypes.ARF.value
    )

    assert mock_service.zip_file_name == f"patient-record-{TEST_NHS_NUMBER}.zip"
    assert response == MOCK_PRESIGNED_URL_RESPONSE


def test_create_document_manifest_presigned_url_lloyd_george(mock_service):
    mock_service.s3_service.create_download_presigned_url.return_value = (
        MOCK_PRESIGNED_URL_RESPONSE
    )
    mock_service.document_service.fetch_available_document_references_by_type.return_value = (
        TEST_LLOYD_GEORGE_DOCUMENT_REFS
    )

    response = mock_service.create_document_manifest_presigned_url(
        SupportedDocumentTypes.LG.value
    )

    assert mock_service.zip_file_name == f"patient-record-{TEST_NHS_NUMBER}.zip"
    assert response == MOCK_PRESIGNED_URL_RESPONSE


def test_create_document_manifest_presigned_url_all(mock_service):
    mock_service.s3_service.create_download_presigned_url.return_value = (
        MOCK_PRESIGNED_URL_RESPONSE
    )
    mock_service.document_service.fetch_available_document_references_by_type.return_value = (
        TEST_DOC_STORE_DOCUMENT_REFS + TEST_LLOYD_GEORGE_DOCUMENT_REFS
    )

    response = mock_service.create_document_manifest_presigned_url(
        SupportedDocumentTypes.LG.value
    )

    assert mock_service.zip_file_name == f"patient-record-{TEST_NHS_NUMBER}.zip"
    assert response == MOCK_PRESIGNED_URL_RESPONSE


def test_create_document_manifest_presigned_raises_exception_when_validation_error(
    mock_service, validation_error
):
    mock_service.document_service.fetch_available_document_references_by_type.side_effect = (
        validation_error
    )

    with pytest.raises(DocumentManifestServiceException):
        mock_service.create_document_manifest_presigned_url(
            SupportedDocumentTypes.ALL.value
        )


def test_create_document_manifest_presigned_raises_exception_when_documents_empty(
    mock_service,
):
    mock_service.document_service.fetch_available_document_references_by_type.return_value = (
        []
    )

    with pytest.raises(DocumentManifestServiceException):
        mock_service.create_document_manifest_presigned_url(
            SupportedDocumentTypes.ALL.value
        )


def test_download_documents_to_be_zipped_handles_duplicate_file_names(mock_service):
    mock_service.documents = TEST_LLOYD_GEORGE_DOCUMENT_REFS

    mock_service.documents[0].file_name = "test.pdf"
    mock_service.documents[1].file_name = "test.pdf"
    mock_service.documents[2].file_name = "test.pdf"

    mock_service.download_documents_to_be_zipped()

    assert mock_service.documents[0].file_name == "test.pdf"
    assert mock_service.documents[1].file_name == "test(2).pdf"
    assert mock_service.documents[2].file_name == "test(3).pdf"


def test_download_documents_to_be_zipped_calls_download_file(mock_service):
    mock_service.documents = TEST_LLOYD_GEORGE_DOCUMENT_REFS

    mock_service.download_documents_to_be_zipped()

    assert mock_service.s3_service.download_file.call_count == 3


def test_download_documents_to_be_zipped_creates_download_path(mock_service):
    mock_service.documents = [TEST_DOC_STORE_DOCUMENT_REFS[0]]
    expected_download_path = os.path.join(
        mock_service.temp_downloads_dir, TEST_DOC_STORE_DOCUMENT_REFS[0].file_name
    )
    expected_document_file_key = TEST_DOC_STORE_DOCUMENT_REFS[0].get_file_key()

    mock_service.download_documents_to_be_zipped()
    mock_service.s3_service.download_file.assert_called_with(
        MOCK_BUCKET, expected_document_file_key, expected_download_path
    )
