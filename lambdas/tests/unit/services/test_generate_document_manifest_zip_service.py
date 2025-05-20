import io
import shutil
import zipfile

import pytest
from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from enums.trace_status import TraceStatus
from models.zip_trace import DocumentManifestZipTrace
from services.generate_document_manifest_zip_service import DocumentManifestZipService
from utils.exceptions import InvalidDocumentReferenceException
from utils.lambda_exceptions import GenerateManifestZipException

from ..conftest import (
    MOCK_BUCKET,
    TEST_DOCUMENT_LOCATION,
    TEST_FILE_KEY,
    TEST_FILE_NAME,
    TEST_NHS_NUMBER,
    TEST_UUID,
)

# from unittest.mock import call


TEST_TIME = "2024-07-02T15:00:00.000000Z"
TEST_DYNAMO_RESPONSE = {
    "ID": TEST_UUID,
    "JobId": TEST_UUID,
    "FilesToDownload": {
        TEST_DOCUMENT_LOCATION: TEST_FILE_NAME,
        f"{TEST_DOCUMENT_LOCATION}2": f"{TEST_FILE_KEY}2",
    },
    "NhsNumber": TEST_NHS_NUMBER,
    "JobStatus": TraceStatus.PENDING.value,
    "Created": TEST_TIME,
}

TEST_ZIP_TRACE = DocumentManifestZipTrace.model_validate(TEST_DYNAMO_RESPONSE)


@pytest.fixture
def mock_service(mocker, set_env, mock_temp_folder):
    service = DocumentManifestZipService(TEST_ZIP_TRACE)
    mocker.patch.object(service, "s3_service")
    mocker.patch.object(service, "dynamo_service")
    yield service


@pytest.fixture
def mock_s3_service(mock_service, mocker):
    mock_s3_service = mock_service.s3_service
    # mocker.patch.object(mock_s3_service, "download_file")
    # mocker.patch.object(mock_s3_service, "upload_file")
    yield mock_s3_service


@pytest.fixture
def mock_dynamo_service(mock_service, mocker):
    mock_dynamo_service = mock_service.dynamo_service
    mocker.patch.object(mock_dynamo_service, "update_item")
    yield mock_dynamo_service


@pytest.fixture
def mock_stream_context_manager():
    def _stream_context_manager(file_content: bytes):
        class stream_context_manager:
            def __enter__(self):
                return io.BytesIO(file_content)

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

        return stream_context_manager()

    return _stream_context_manager


# def test_download_documents_to_be_zipped(mocker, mock_service):
#     mock_service.download_file_from_s3 = mocker.MagicMock()
#     mock_service.download_documents_to_be_zipped()
#
#     calls = [
#         call(TEST_FILE_NAME, TEST_DOCUMENT_LOCATION),
#         call(f"{TEST_FILE_KEY}2", f"{TEST_DOCUMENT_LOCATION}2"),
#     ]
#
#     mock_service.download_file_from_s3.assert_has_calls(calls)


# def test_download_file_from_s3(mock_service, mock_s3_service):
#     mock_service.download_file_from_s3(TEST_FILE_NAME, TEST_DOCUMENT_LOCATION)
#
#     mock_s3_service.download_file.assert_called_once_with(
#         MOCK_BUCKET,
#         TEST_FILE_KEY,
#         f"{mock_service.temp_downloads_dir}/{TEST_FILE_NAME}",
#     )
#     assert mock_service.zip_trace_object.job_status != TraceStatus.FAILED
#
#
# def test_download_file_from_s3_raises_exception(mock_service, mock_s3_service):
#     mock_s3_service.download_file.side_effect = ClientError(
#         {"Error": {"Code": "500", "Message": "test error"}}, "testing"
#     )
#
#     with pytest.raises(GenerateManifestZipException) as e:
#         mock_service.download_file_from_s3(TEST_FILE_NAME, TEST_DOCUMENT_LOCATION)
#
#     mock_s3_service.download_file.assert_called_once_with(
#         MOCK_BUCKET,
#         TEST_FILE_KEY,
#         f"{mock_service.temp_downloads_dir}/{TEST_FILE_NAME}",
#     )
#     assert e.value == GenerateManifestZipException(
#         500, LambdaError.ZipServiceClientError
#     )
#     assert mock_service.zip_trace_object.job_status == TraceStatus.FAILED


def test_get_file_bucket_and_key_returns_correct_items(mock_service):
    zip_trace_object = mock_service.zip_trace_object
    documents = zip_trace_object.files_to_download
    file_location = list(documents.keys())[0]
    expected = (MOCK_BUCKET, TEST_FILE_KEY)

    assert mock_service.get_file_bucket_and_key(file_location) == expected


def test_get_file_bucket_and_key_throws_exception_when_not_passed_incorrect_format(
    mock_service,
):
    bad_location = "Not a location"

    with pytest.raises(InvalidDocumentReferenceException) as e:
        mock_service.get_file_bucket_and_key(bad_location)

    assert e.value.args[0] == "Failed to parse bucket from file location string"
    assert mock_service.zip_trace_object.job_status == TraceStatus.FAILED


def test_upload_zip_file(mocker, mock_service, mock_s3_service):
    zip_buffer = io.BytesIO(b"Fake ZIP content")
    zip_buffer.seek(0)

    mock_upload = mocker.patch.object(mock_s3_service, "upload_file_obj")

    mock_service.upload_zip_file(zip_buffer)

    expected_key = mock_service.zip_file_name
    expected_location = f"s3://{mock_service.zip_output_bucket}/{expected_key}"

    mock_upload.assert_called_once_with(
        zip_buffer, mock_service.zip_output_bucket, expected_key
    )

    assert mock_service.zip_trace_object.zip_file_location == expected_location
    assert mock_service.zip_trace_object.job_status == TraceStatus.COMPLETED


def test_upload_zip_file_raises_exception(mocker, mock_service, mock_s3_service):
    zip_buffer = io.BytesIO(b"Fake ZIP content")
    zip_buffer.seek(0)

    error_response = {"Error": {"Code": "500", "Message": "test error"}}
    mocker.patch.object(
        mock_s3_service,
        "upload_file_obj",
        side_effect=ClientError(error_response, "UploadObject"),
    )

    with pytest.raises(GenerateManifestZipException) as exc_info:
        mock_service.upload_zip_file(zip_buffer)

    expected_key = mock_service.zip_file_name
    expected_location = f"s3://{mock_service.zip_output_bucket}/{expected_key}"

    assert mock_service.zip_trace_object.zip_file_location == expected_location
    assert mock_service.zip_trace_object.job_status == TraceStatus.FAILED
    exception = exc_info.value
    assert isinstance(exception, GenerateManifestZipException)
    assert exception.status_code == 500
    assert exception.error == LambdaError.ZipServiceClientError


def test_update_dynamo(mock_service, mock_dynamo_service):
    mock_service.update_dynamo_with_fields({"job_status"})

    mock_dynamo_service.update_item.assert_called_once_with(
        table_name="test_zip_table",
        key_pair={"ID": mock_service.zip_trace_object.id},
        updated_fields=mock_service.zip_trace_object.model_dump(
            by_alias=True, include={"job_status"}
        ),
    )


def test_update_processing_status(mock_service):
    mock_service.update_processing_status()
    assert mock_service.zip_trace_object.job_status == TraceStatus.PROCESSING


def test_update_failed_status(mock_service):
    mock_service.update_failed_status()
    assert mock_service.zip_trace_object.job_status == TraceStatus.FAILED


def test_stream_zip_documents(
    mocker, mock_service, mock_s3_service, mock_stream_context_manager
):
    file_content = b"Dummy file content"

    mock_s3_service.get_object_stream.return_value = mock_stream_context_manager(
        file_content
    )
    mock_copyfileobj = mocker.patch("shutil.copyfileobj", wraps=shutil.copyfileobj)

    zip_buffer = mock_service.stream_zip_documents()

    expected_files = list(mock_service.zip_trace_object.files_to_download.values())

    with zipfile.ZipFile(zip_buffer, "r") as zipf:
        file_list = zipf.namelist()
        assert sorted(file_list) == sorted(expected_files)

        for file_name in expected_files:
            with zipf.open(file_name) as f:
                assert f.read() == file_content

    assert mock_copyfileobj.called


def test_stream_zip_documents_raises_client_error(
    mocker, mock_service, mock_s3_service
):
    from botocore.exceptions import ClientError

    mock_s3_service.get_object_stream.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "S3 error"}}, "GetObject"
    )

    mocker.patch.object(
        mock_service, "get_file_bucket_and_key", return_value=("bucket", "key")
    )

    with pytest.raises(GenerateManifestZipException) as exc_info:
        mock_service.stream_zip_documents()

    assert exc_info.value.error == LambdaError.ZipServiceClientError
    assert exc_info.value.status_code == 500
    assert mock_service.zip_trace_object.job_status == TraceStatus.FAILED


def test_stream_zip_documents_raises_zip_creation_error(
    mocker, mock_service, mock_s3_service, mock_stream_context_manager
):
    file_content = b"Dummy file content"

    mock_s3_service.get_object_stream.return_value = mock_stream_context_manager(
        file_content
    )
    mocker.patch.object(
        mock_service, "get_file_bucket_and_key", return_value=("bucket", "key")
    )
    mocker.patch("zipfile.ZipFile.__enter__", side_effect=OSError("Disk error"))

    with pytest.raises(GenerateManifestZipException) as exc_info:
        mock_service.stream_zip_documents()

    assert exc_info.value.error == LambdaError.ZipCreationError
    assert exc_info.value.status_code == 500
    assert mock_service.zip_trace_object.job_status == TraceStatus.FAILED
