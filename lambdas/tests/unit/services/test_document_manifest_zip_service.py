import pytest
from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from enums.zip_trace import ZipTraceStatus
from models.zip_trace import DocumentManifestZipTrace
from services.document_manifest_zip_service import DocumentManifestZipService
from utils.exceptions import InvalidDocumentReferenceException
from utils.lambda_exceptions import DocumentManifestServiceException

from ..conftest import (
    MOCK_BUCKET,
    MOCK_ZIP_OUTPUT_BUCKET,
    TEST_DOCUMENT_LOCATION,
    TEST_FILE_KEY,
    TEST_FILE_NAME,
    TEST_UUID,
)

Response_for_handler = {
    "ID": {"S": "97d79b0e-31f6-49d9-b882-b3d2c8308b2c"},
    "Created": {"S": "2024-07-02T13:11:00.544608Z"},
    "FilesToDownload": {
        "M": {
            "s3://ndrc-lloyd-george-store/9000000004/aefbfb37-6e52-4de": {
                "S": "1of5_Lloyd_George_Record(2).pdf"
            },
            "s3://ndrc-lloyd-george-store/9000000004/f2a8e23d-80b1-4682": {
                "S": "1of5_Lloyd_George_Record.pdf"
            },
        }
    },
    "JobId": {"S": "e9653b17-203f-4a9b-81b5-1cb71eb10423"},
    "Status": {"S": "Pending"},
}
TEST_TIME = "2024-07-02T15:00:00.000000Z"
TEST_DYNAMO_RESPONSE = {
    "ID": TEST_UUID,
    "JobId": TEST_UUID,
    "FilesToDownload": {TEST_DOCUMENT_LOCATION: TEST_FILE_NAME},
    "Status": ZipTraceStatus.PENDING.value,
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
    mocker.patch.object(mock_s3_service, "download_file")
    mocker.patch.object(mock_s3_service, "upload_file")
    yield mock_s3_service


@pytest.fixture
def mock_dynamo_service(mock_service, mocker):
    mock_dynamo_service = mock_service.dynamo_service
    mocker.patch.object(mock_dynamo_service, "update_item")
    yield mock_dynamo_service


def test_download_file_from_s3(mock_service, mock_s3_service):
    mock_service.download_file_from_s3(TEST_FILE_NAME, TEST_DOCUMENT_LOCATION)

    mock_s3_service.download_file.assert_called_once_with(
        MOCK_BUCKET,
        TEST_FILE_KEY,
        f"{mock_service.temp_downloads_dir}/{TEST_FILE_NAME}",
    )
    assert mock_service.zip_trace_object.status != ZipTraceStatus.FAILED.value


def test_download_file_from_s3_raises_exception(mock_service, mock_s3_service):
    mock_s3_service.download_file.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "test error"}}, "testing"
    )

    with pytest.raises(DocumentManifestServiceException) as e:
        mock_service.download_file_from_s3(TEST_FILE_NAME, TEST_DOCUMENT_LOCATION)

    mock_s3_service.download_file.assert_called_once_with(
        MOCK_BUCKET,
        TEST_FILE_KEY,
        f"{mock_service.temp_downloads_dir}/{TEST_FILE_NAME}",
    )
    assert e.value == DocumentManifestServiceException(
        500, LambdaError.ZipServiceClientError
    )
    assert mock_service.zip_trace_object.status == ZipTraceStatus.FAILED.value


def test_get_file_bucket_and_key_returns_correct_items(mock_service):
    zip_trace_object = mock_service.zip_trace_object
    documents = zip_trace_object.files_to_download
    file_location = list(documents.keys())[0]
    expected = (MOCK_BUCKET, TEST_FILE_KEY)

    assert mock_service.get_file_bucket_and_key(file_location) == expected


def test_get_file_bucket_and_key_throws_exeception_when_not_passed_incorrect_fomat(
    mock_service,
):
    bad_location = "Not a location"

    with pytest.raises(InvalidDocumentReferenceException) as e:
        mock_service.get_file_bucket_and_key(bad_location)

    assert e.value.args[0] == "Failed to parse bucket from file location string"
    assert mock_service.zip_trace_object.status == ZipTraceStatus.FAILED.value


def test_upload_zip_file(mock_service, mock_s3_service):
    mock_service.upload_zip_file()

    mock_s3_service.upload_file.assert_called_once_with(
        file_name=f"{mock_service.temp_output_dir}/{mock_service.zip_file_name}",
        s3_bucket_name=MOCK_ZIP_OUTPUT_BUCKET,
        file_key=mock_service.zip_file_name,
    )
    assert (
        mock_service.zip_trace_object.zip_file_location
        == f"s3://{MOCK_ZIP_OUTPUT_BUCKET}/{mock_service.zip_file_name}"
    )
    assert mock_service.zip_trace_object.status == ZipTraceStatus.COMPLETED.value


def test_upload_zip_file_throws_exception_on_error(mock_service, mock_s3_service):
    mock_s3_service.upload_file.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "test error"}}, "testing"
    )

    with pytest.raises(DocumentManifestServiceException) as e:
        mock_service.upload_zip_file()

    mock_s3_service.upload_file.assert_called_once_with(
        file_name=f"{mock_service.temp_output_dir}/{mock_service.zip_file_name}",
        s3_bucket_name=MOCK_ZIP_OUTPUT_BUCKET,
        file_key=mock_service.zip_file_name,
    )
    assert e.value == DocumentManifestServiceException(
        500, LambdaError.ZipServiceClientError
    )
    assert mock_service.zip_trace_object.status == ZipTraceStatus.FAILED.value


def test_update_dynamo(mock_service, mock_dynamo_service):
    # mock_service.zip_trace_object.status = ZipTraceStatus.COMPLETED.value
    mock_service.update_dynamo_with_fields({"status"})

    mock_dynamo_service.update_item.assert_called_once_with(
        "test_zip_table",
        mock_service.zip_trace_object.id,
        mock_service.zip_trace_object.model_dump(by_alias=True, include={"status"}),
    )


def test_update_processing_status(mock_service):
    mock_service.update_processing_status()
    assert mock_service.zip_trace_object.status == ZipTraceStatus.PROCESSING.value


def test_update_failed_status(mock_service):
    mock_service.update_failed_status()
    assert mock_service.zip_trace_object.status == ZipTraceStatus.FAILED.value
