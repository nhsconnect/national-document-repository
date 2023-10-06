import os

from models.document import Document
from services.document_manifest_service import DocumentManifestService
from tests.unit.conftest import (MOCK_BUCKET, MOCK_ZIP_OUTPUT_BUCKET,
                                 MOCK_ZIP_TRACE_TABLE, TEST_DOCUMENT_LOCATION,
                                 TEST_FILE_NAME, TEST_NHS_NUMBER,
                                 TEST_VIRUS_SCANNER_RESULT)

MOCK_DOCUMENTS = [
    Document(
        "123456789", TEST_FILE_NAME, TEST_VIRUS_SCANNER_RESULT, TEST_DOCUMENT_LOCATION
    ),
    Document(
        "123222222", TEST_FILE_NAME, TEST_VIRUS_SCANNER_RESULT, TEST_DOCUMENT_LOCATION
    ),
    Document(
        "123456789", TEST_FILE_NAME, TEST_VIRUS_SCANNER_RESULT, TEST_DOCUMENT_LOCATION
    ),
]

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
        TEST_NHS_NUMBER, MOCK_DOCUMENTS, MOCK_ZIP_OUTPUT_BUCKET, MOCK_ZIP_TRACE_TABLE
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

    service = DocumentManifestService(
        TEST_NHS_NUMBER, MOCK_DOCUMENTS, MOCK_ZIP_OUTPUT_BUCKET, MOCK_ZIP_TRACE_TABLE
    )

    service.download_documents_to_be_zipped()

    document_one_name = MOCK_DOCUMENTS[0].file_name
    document_two_name = MOCK_DOCUMENTS[1].file_name
    document_three_name = MOCK_DOCUMENTS[2].file_name

    assert document_one_name == "test.pdf"
    assert document_two_name == "test(2).pdf"
    assert document_three_name == "test(3).pdf"


def test_download_documents_to_be_zipped_calls_download_file(set_env, mocker):
    mocker.patch("boto3.client")

    service = DocumentManifestService(
        TEST_NHS_NUMBER, MOCK_DOCUMENTS, MOCK_ZIP_OUTPUT_BUCKET, MOCK_ZIP_TRACE_TABLE
    )
    mock_s3_service_download_file = mocker.patch.object(
        service.s3_service, "download_file"
    )

    service.download_documents_to_be_zipped()

    assert mock_s3_service_download_file.call_count == 3


def test_download_documents_to_be_zipped_creates_download_path(set_env, mocker):
    mocker.patch("boto3.client")
    mock_document = [
        Document(
            "123456789",
            TEST_FILE_NAME,
            TEST_VIRUS_SCANNER_RESULT,
            TEST_DOCUMENT_LOCATION,
        )
    ]

    service = DocumentManifestService(
        TEST_NHS_NUMBER, mock_document, MOCK_ZIP_OUTPUT_BUCKET, MOCK_ZIP_TRACE_TABLE
    )
    mock_s3_service_download_file = mocker.patch.object(
        service.s3_service, "download_file"
    )

    service.download_documents_to_be_zipped()

    if is_windows():
        expected_download_path = (
            f"{service.temp_downloads_dir}\\{MOCK_DOCUMENTS[0].file_name}"
        )
    else:
        expected_download_path = (
            f"{service.temp_downloads_dir}/{MOCK_DOCUMENTS[0].file_name}"
        )
    document_file_key = MOCK_DOCUMENTS[0].file_key

    mock_s3_service_download_file.assert_called_with(
        MOCK_BUCKET, document_file_key, expected_download_path
    )


def is_windows():
    if os.name == "nt":
        return True
    return False
