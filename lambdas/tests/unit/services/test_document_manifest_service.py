import os
from copy import copy

import pytest
from enums.supported_document_types import SupportedDocumentTypes
from services.document_manifest_service import DocumentManifestService
from tests.unit.conftest import MOCK_BUCKET, MOCK_ZIP_OUTPUT_BUCKET, TEST_NHS_NUMBER
from tests.unit.helpers.data.s3_responses import MOCK_PRESIGNED_URL_RESPONSE
from tests.unit.helpers.data.test_documents import (
    create_test_doc_store_refs,
    create_test_lloyd_george_doc_store_refs,
)
from utils.common_query_filters import UploadCompleted
from utils.lambda_exceptions import DocumentManifestServiceException

TEST_DOC_STORE_DOCUMENT_REFS = create_test_doc_store_refs()
TEST_LLOYD_GEORGE_DOCUMENT_REFS = create_test_lloyd_george_doc_store_refs()


@pytest.fixture
def mock_service(mocker, set_env):
    service = DocumentManifestService(TEST_NHS_NUMBER)
    mocker.patch.object(service, "s3_service")
    mocker.patch.object(service, "dynamo_service")
    mocker.patch.object(service, "document_service")
    yield service


@pytest.fixture
def mock_document_service(mocker, mock_service):
    mock_document_service = mock_service.document_service
    mocker.patch.object(
        mock_document_service, "fetch_available_document_references_by_type"
    )
    yield mock_document_service


@pytest.fixture
def mock_s3_service(mocker, mock_service):
    mock_s3_service = mock_service.s3_service
    mocker.patch.object(mock_s3_service, "create_download_presigned_url")
    mocker.patch.object(mock_s3_service, "upload_file")
    mock_s3_service.create_download_presigned_url.return_value = (
        MOCK_PRESIGNED_URL_RESPONSE
    )
    yield mock_s3_service


@pytest.fixture
def mock_dynamo_service(mocker, mock_service):
    mock_dynamo_service = mock_service.dynamo_service
    mocker.patch.object(mock_dynamo_service, "create_item")
    yield mock_dynamo_service


def test_create_document_manifest_presigned_url_doc_store(
    mock_service, mock_s3_service, mock_document_service
):
    mock_document_service.fetch_available_document_references_by_type.return_value = (
        TEST_DOC_STORE_DOCUMENT_REFS
    )

    response = mock_service.create_document_manifest_presigned_url(
        SupportedDocumentTypes.ARF
    )
    assert mock_service.zip_file_name == f"patient-record-{TEST_NHS_NUMBER}.zip"
    assert response == MOCK_PRESIGNED_URL_RESPONSE
    mock_document_service.fetch_available_document_references_by_type.assert_called_once_with(
        nhs_number=TEST_NHS_NUMBER,
        doc_type=SupportedDocumentTypes.ARF,
        query_filter=UploadCompleted,
    )
    mock_s3_service.create_download_presigned_url.assert_called_once_with(
        s3_bucket_name=MOCK_ZIP_OUTPUT_BUCKET, file_key=mock_service.zip_file_name
    )


def test_create_document_manifest_presigned_url_lloyd_george(
    mock_service, mock_s3_service, mock_document_service
):
    mock_service.document_service.fetch_available_document_references_by_type.return_value = (
        TEST_LLOYD_GEORGE_DOCUMENT_REFS
    )

    response = mock_service.create_document_manifest_presigned_url(
        SupportedDocumentTypes.LG
    )

    assert mock_service.zip_file_name == f"patient-record-{TEST_NHS_NUMBER}.zip"
    assert response == MOCK_PRESIGNED_URL_RESPONSE
    mock_document_service.fetch_available_document_references_by_type.assert_called_once_with(
        nhs_number=TEST_NHS_NUMBER,
        doc_type=SupportedDocumentTypes.LG,
        query_filter=UploadCompleted,
    )
    mock_s3_service.create_download_presigned_url.assert_called_once_with(
        s3_bucket_name=MOCK_ZIP_OUTPUT_BUCKET, file_key=mock_service.zip_file_name
    )


def test_create_document_manifest_presigned_url_all(
    mock_service, mock_s3_service, mock_document_service
):
    mock_service.document_service.fetch_available_document_references_by_type.return_value = (
        TEST_DOC_STORE_DOCUMENT_REFS + TEST_LLOYD_GEORGE_DOCUMENT_REFS
    )

    response = mock_service.create_document_manifest_presigned_url(
        SupportedDocumentTypes.ALL
    )

    assert mock_service.zip_file_name == f"patient-record-{TEST_NHS_NUMBER}.zip"
    assert response == MOCK_PRESIGNED_URL_RESPONSE
    mock_document_service.fetch_available_document_references_by_type.assert_called_once_with(
        nhs_number=TEST_NHS_NUMBER,
        doc_type=SupportedDocumentTypes.ALL,
        query_filter=UploadCompleted,
    )
    mock_s3_service.create_download_presigned_url.assert_called_once_with(
        s3_bucket_name=MOCK_ZIP_OUTPUT_BUCKET, file_key=mock_service.zip_file_name
    )


def test_create_document_manifest_presigned_raises_exception_when_validation_error(
    mock_service, validation_error
):
    mock_service.document_service.fetch_available_document_references_by_type.side_effect = (
        validation_error
    )

    with pytest.raises(DocumentManifestServiceException):
        mock_service.create_document_manifest_presigned_url(SupportedDocumentTypes.ALL)


def test_create_document_manifest_presigned_raises_exception_when_uploading_in_process(
    mock_service, validation_error
):
    file_in_progress = copy(TEST_LLOYD_GEORGE_DOCUMENT_REFS[0])
    file_in_progress.uploaded = False
    file_in_progress.uploading = True

    mock_service.document_service.fetch_available_document_references_by_type.return_value = [
        file_in_progress
    ]

    with pytest.raises(DocumentManifestServiceException) as e:
        mock_service.create_document_manifest_presigned_url(SupportedDocumentTypes.LG)

    assert e.value.status_code == 423
    assert e.value.err_code == "LGL_423"


def test_create_document_manifest_presigned_raises_exception_when_not_all_files_uploaded(
    mock_service, validation_error
):
    mock_service.document_service.fetch_available_document_references_by_type.return_value = TEST_LLOYD_GEORGE_DOCUMENT_REFS[
        0:1
    ]

    with pytest.raises(DocumentManifestServiceException):
        mock_service.create_document_manifest_presigned_url(SupportedDocumentTypes.LG)


def test_create_document_manifest_presigned_raises_exception_when_documents_empty(
    mock_service,
):
    mock_service.document_service.fetch_available_document_references_by_type.return_value = (
        []
    )

    with pytest.raises(DocumentManifestServiceException):
        mock_service.create_document_manifest_presigned_url(SupportedDocumentTypes.ALL)


def test_download_documents_to_be_zipped_handles_duplicate_file_names(mock_service):
    mock_service.documents = TEST_LLOYD_GEORGE_DOCUMENT_REFS

    mock_service.documents[0].file_name = "test.pdf"
    mock_service.documents[1].file_name = "test.pdf"
    mock_service.documents[2].file_name = "test.pdf"

    mock_service.download_documents_to_be_zipped(TEST_LLOYD_GEORGE_DOCUMENT_REFS)

    assert mock_service.documents[0].file_name == "test.pdf"
    assert mock_service.documents[1].file_name == "test(2).pdf"
    assert mock_service.documents[2].file_name == "test(3).pdf"


def test_download_documents_to_be_zipped_calls_download_file(
    mock_service, mock_s3_service
):
    mock_service.download_documents_to_be_zipped(TEST_LLOYD_GEORGE_DOCUMENT_REFS)

    assert mock_s3_service.download_file.call_count == 3


def test_download_documents_to_be_zipped_creates_download_path(
    mock_service, mock_s3_service
):
    expected_download_path = os.path.join(
        mock_service.temp_downloads_dir, TEST_DOC_STORE_DOCUMENT_REFS[0].file_name
    )
    expected_document_file_key = TEST_DOC_STORE_DOCUMENT_REFS[0].get_file_key()

    mock_service.download_documents_to_be_zipped([TEST_DOC_STORE_DOCUMENT_REFS[0]])
    mock_s3_service.download_file.assert_called_with(
        MOCK_BUCKET, expected_document_file_key, expected_download_path
    )


def test_upload_zip_file(mock_service, mock_s3_service, mock_dynamo_service):
    expected_upload_path = os.path.join(
        mock_service.temp_output_dir, mock_service.zip_file_name
    )
    mock_service.upload_zip_file()

    mock_s3_service.upload_file.assert_called_with(
        file_name=expected_upload_path,
        s3_bucket_name=MOCK_ZIP_OUTPUT_BUCKET,
        file_key=mock_service.zip_file_name,
    )

    mock_dynamo_service.create_item.assert_called_once()
