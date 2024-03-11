import pytest
from botocore.exceptions import ClientError
from services.upload_confirm_result_service import UploadConfirmResultService
from tests.unit.conftest import (
    MOCK_ARF_BUCKET,
    MOCK_ARF_TABLE_NAME,
    MOCK_LG_BUCKET,
    MOCK_LG_STAGING_STORE_BUCKET,
    MOCK_LG_TABLE_NAME,
    TEST_FILE_KEY,
    TEST_NHS_NUMBER,
)
from tests.unit.helpers.data.upload_confirm_result import (
    MOCK_ARF_DOCUMENT_REFERENCES,
    MOCK_ARF_DOCUMENTS,
    MOCK_BOTH_DOC_TYPES,
    MOCK_LG_DOCUMENT_REFERENCES,
    MOCK_LG_DOCUMENTS,
    MOCK_NO_DOC_TYPE,
)
from utils.lambda_exceptions import UploadConfirmResultException


@pytest.fixture
def patched_service(set_env, mocker):
    service = UploadConfirmResultService(TEST_NHS_NUMBER)
    mock_dynamo_service = mocker.patch.object(service, "dynamo_service")
    mocker.patch.object(mock_dynamo_service, "update_item")
    mocker.patch.object(mock_dynamo_service, "scan_table")
    mock_s3_service = mocker.patch.object(service, "s3_service")
    mocker.patch.object(mock_s3_service, "copy_across_bucket")
    mocker.patch.object(mock_s3_service, "delete_object")
    yield service


@pytest.fixture
def mock_validate_number_of_documents(patched_service, mocker):
    yield mocker.patch.object(patched_service, "validate_number_of_documents")


@pytest.fixture
def mock_move_files_and_update_dynamo(patched_service, mocker):
    yield mocker.patch.object(patched_service, "move_files_and_update_dynamo")


@pytest.fixture
def mock_update_dynamo_table(patched_service, mocker):
    yield mocker.patch.object(patched_service, "update_dynamo_table")


@pytest.fixture
def mock_copy_files_from_staging_bucket(patched_service, mocker):
    yield mocker.patch.object(patched_service, "copy_files_from_staging_bucket")


@pytest.fixture
def mock_delete_file_from_staging_bucket(patched_service, mocker):
    yield mocker.patch.object(patched_service, "delete_file_from_staging_bucket")


def test_process_documents_with_lg_document_references(
    patched_service,
    mock_validate_number_of_documents,
    mock_move_files_and_update_dynamo,
):
    patched_service.process_documents(MOCK_LG_DOCUMENTS)

    mock_validate_number_of_documents.assert_called_with(
        MOCK_LG_TABLE_NAME, MOCK_LG_DOCUMENT_REFERENCES
    )
    mock_move_files_and_update_dynamo.assert_called_with(
        MOCK_LG_DOCUMENT_REFERENCES, MOCK_LG_BUCKET, MOCK_LG_TABLE_NAME
    )


def test_process_documents_with_arf_document_references(
    patched_service,
    mock_validate_number_of_documents,
    mock_move_files_and_update_dynamo,
):
    patched_service.process_documents(MOCK_ARF_DOCUMENTS)

    mock_validate_number_of_documents.assert_not_called()
    mock_move_files_and_update_dynamo.assert_called_with(
        MOCK_ARF_DOCUMENT_REFERENCES, MOCK_ARF_BUCKET, MOCK_ARF_TABLE_NAME
    )


def test_process_documents_with_both_types_of_document_references(
    patched_service,
    mock_validate_number_of_documents,
    mock_move_files_and_update_dynamo,
):
    patched_service.process_documents(MOCK_BOTH_DOC_TYPES)

    mock_validate_number_of_documents.assert_called_once_with(
        MOCK_LG_TABLE_NAME, [TEST_FILE_KEY]
    )
    assert mock_move_files_and_update_dynamo.call_count == 2


def test_process_documents_when_no_lg_or_arf_doc_type_in_documents_raises_exception(
    patched_service,
    mock_validate_number_of_documents,
    mock_move_files_and_update_dynamo,
):
    with pytest.raises(UploadConfirmResultException):
        patched_service.process_documents(MOCK_NO_DOC_TYPE)

    mock_validate_number_of_documents.assert_not_called()
    mock_move_files_and_update_dynamo.assert_not_called()


def test_process_documents_when_dynamo_throws_error(
    patched_service, mock_update_dynamo_table
):
    mock_update_dynamo_table.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "test error"}}, "testing"
    )

    with pytest.raises(UploadConfirmResultException):
        patched_service.process_documents(MOCK_ARF_DOCUMENTS)


def test_move_files_and_update_dynamo(
    patched_service,
    mock_copy_files_from_staging_bucket,
    mock_delete_file_from_staging_bucket,
    mock_update_dynamo_table,
):
    patched_service.move_files_and_update_dynamo(
        MOCK_ARF_DOCUMENT_REFERENCES, MOCK_ARF_BUCKET, MOCK_ARF_TABLE_NAME
    )

    mock_copy_files_from_staging_bucket.assert_called_once_with(
        MOCK_ARF_DOCUMENT_REFERENCES, MOCK_ARF_BUCKET
    )
    mock_delete_file_from_staging_bucket.assert_called_with(TEST_FILE_KEY)
    mock_update_dynamo_table.assert_called_with(
        MOCK_ARF_TABLE_NAME, TEST_FILE_KEY, MOCK_ARF_BUCKET
    )
    assert mock_delete_file_from_staging_bucket.call_count == 2
    assert mock_update_dynamo_table.call_count == 2


def test_copy_files_from_staging_bucket(patched_service):
    patched_service.copy_files_from_staging_bucket(
        MOCK_ARF_DOCUMENT_REFERENCES, MOCK_ARF_BUCKET
    )

    assert patched_service.s3_service.copy_across_bucket.call_count == 2


def test_delete_file_from_staging_bucket(patched_service):
    patched_service.delete_file_from_staging_bucket(TEST_FILE_KEY)

    patched_service.s3_service.delete_object.assert_called_with(
        MOCK_LG_STAGING_STORE_BUCKET, TEST_FILE_KEY
    )


def test_update_dynamo_table(patched_service):
    file_location = f"s3://{MOCK_ARF_BUCKET}/{TEST_NHS_NUMBER}/{TEST_FILE_KEY}"

    patched_service.update_dynamo_table(
        MOCK_ARF_TABLE_NAME, TEST_FILE_KEY, MOCK_ARF_BUCKET
    )

    patched_service.dynamo_service.update_item.assert_called_with(
        MOCK_ARF_TABLE_NAME,
        TEST_FILE_KEY,
        {"Uploaded": True, "FileLocation": file_location},
    )


def test_validate_number_of_documents_success(patched_service):
    patched_service.dynamo_service.scan_table.return_value = {"Items": ["doc1"]}

    patched_service.validate_number_of_documents(
        MOCK_LG_TABLE_NAME, MOCK_LG_DOCUMENT_REFERENCES
    )

    patched_service.dynamo_service.scan_table.assert_called_once()


def test_validate_number_of_documents_raises_exception(patched_service):
    patched_service.dynamo_service.scan_table.return_value = {"Items": ["doc1", "doc2"]}

    with pytest.raises(UploadConfirmResultException):
        patched_service.validate_number_of_documents(
            MOCK_LG_TABLE_NAME, MOCK_LG_DOCUMENT_REFERENCES
        )

    patched_service.dynamo_service.scan_table.assert_called_once()
