import os

from services.document_manifest_service import DocumentManifestService
from tests.unit.conftest import (MOCK_BUCKET, MOCK_ZIP_OUTPUT_BUCKET,
                                 MOCK_ZIP_TRACE_TABLE, TEST_NHS_NUMBER)
from tests.unit.helpers.data.test_documents import create_test_doc_store_refs

TEST_DOC_STORE_REFERENCES = create_test_doc_store_refs()
MOCK_PRESIGNED_URL_RESPONSE = {
    "url": "https://ndr-dev-document-store.s3.amazonaws.com/",
    "fields": {
        "key": "0abed67c-0d0b-4a11-a600-a2f19ee61281",
        "x-amz-algorithm": "AWS4-HMAC-SHA256",
        "x-amz-credential": "ASIAXYSUA44VTL5M5LWL/20230911/eu-west-2/s3/aws4_request",
        "x-amz-date": "20230911T084756Z",
        "x-amz-expires": "1800",
        "x-amz-signed-headers": "test-host",
        "x-amz-signature": "test-signature",
    },
}


def test_create_document_manifest_presigned_url(set_env, mocker):
    mocker.patch("boto3.client")

    service = DocumentManifestService(
        TEST_NHS_NUMBER,
        TEST_DOC_STORE_REFERENCES,
        MOCK_ZIP_OUTPUT_BUCKET,
        MOCK_ZIP_TRACE_TABLE,
    )

    mock_s3_service = mocker.patch.object(
        service.s3_service, "create_download_presigned_url"
    )
    mock_s3_service.return_value = MOCK_PRESIGNED_URL_RESPONSE

    mock_download_documents_to_be_zipped = mocker.patch.object(
        service, "download_documents_to_be_zipped"
    )
    mock_upload_zip_file = mocker.patch.object(service, "upload_zip_file")

    response = service.create_document_manifest_presigned_url()

    assert response == MOCK_PRESIGNED_URL_RESPONSE
    mock_download_documents_to_be_zipped.assert_called_once()
    mock_upload_zip_file.assert_called_once()


def test_download_documents_to_be_zipped_handles_duplicate_file_names(set_env, mocker):
    mocker.patch("boto3.client")

    TEST_DOC_STORE_REFERENCES[0].file_name = "test.pdf"
    TEST_DOC_STORE_REFERENCES[1].file_name = "test.pdf"
    TEST_DOC_STORE_REFERENCES[2].file_name = "test.pdf"

    service = DocumentManifestService(
        TEST_NHS_NUMBER,
        TEST_DOC_STORE_REFERENCES,
        MOCK_ZIP_OUTPUT_BUCKET,
        MOCK_ZIP_TRACE_TABLE,
    )

    service.download_documents_to_be_zipped()

    assert TEST_DOC_STORE_REFERENCES[0].file_name == "test.pdf"
    assert TEST_DOC_STORE_REFERENCES[1].file_name == "test(2).pdf"
    assert TEST_DOC_STORE_REFERENCES[2].file_name == "test(3).pdf"


def test_download_documents_to_be_zipped_calls_download_file(set_env, mocker):
    mocker.patch("boto3.client")

    service = DocumentManifestService(
        TEST_NHS_NUMBER,
        TEST_DOC_STORE_REFERENCES,
        MOCK_ZIP_OUTPUT_BUCKET,
        MOCK_ZIP_TRACE_TABLE,
    )
    mock_s3_service_download_file = mocker.patch.object(
        service.s3_service, "download_file"
    )

    service.download_documents_to_be_zipped()

    assert mock_s3_service_download_file.call_count == 3


def test_download_documents_to_be_zipped_creates_download_path(set_env, mocker):
    mocker.patch("boto3.client")

    service = DocumentManifestService(
        TEST_NHS_NUMBER,
        [TEST_DOC_STORE_REFERENCES[0]],
        MOCK_ZIP_OUTPUT_BUCKET,
        MOCK_ZIP_TRACE_TABLE,
    )
    mock_s3_service_download_file = mocker.patch.object(
        service.s3_service, "download_file"
    )

    service.download_documents_to_be_zipped()

    expected_download_path = os.path.join(
        service.temp_downloads_dir, TEST_DOC_STORE_REFERENCES[0].file_name
    )

    document_file_key = TEST_DOC_STORE_REFERENCES[0].get_file_key()

    mock_s3_service_download_file.assert_called_with(
        MOCK_BUCKET, document_file_key, expected_download_path
    )
