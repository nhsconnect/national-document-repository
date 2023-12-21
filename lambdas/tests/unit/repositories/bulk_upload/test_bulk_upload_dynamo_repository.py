import os

import pytest
from freezegun import freeze_time
from repositories.bulk_upload.bulk_upload_dynamo_repository import (
    BulkUploadDynamoRepository,
)
from tests.unit.conftest import (
    MOCK_BULK_REPORT_TABLE_NAME,
    MOCK_LG_TABLE_NAME,
    TEST_OBJECT_KEY,
)
from tests.unit.helpers.data.bulk_upload.test_data import (
    TEST_DOCUMENT_REFERENCE_LIST,
    TEST_NHS_NUMBER_FOR_BULK_UPLOAD,
    TEST_STAGING_METADATA, TEST_DOCUMENT_REFERENCE,
)


@pytest.fixture
def mock_uuid(mocker):
    test_uuid = TEST_OBJECT_KEY
    mocker.patch("uuid.uuid4", return_value=test_uuid)
    yield test_uuid


@pytest.fixture
def repo_under_test(set_env, mocker):
    repo = BulkUploadDynamoRepository()
    mocker.patch.object(repo, "dynamo_repository")
    yield repo


def test_create_record_in_dynamodb_table(set_env, repo_under_test):
    repo_under_test.create_record_in_lg_dynamo_table(TEST_DOCUMENT_REFERENCE)

    assert TEST_DOCUMENT_REFERENCE in repo_under_test.dynamo_records_in_transaction

    repo_under_test.dynamo_repository.create_item.assert_called_with(
        table_name=MOCK_LG_TABLE_NAME, item=TEST_DOCUMENT_REFERENCE.to_dict()
    )


@freeze_time("2023-10-1 13:00:00")
def test_report_upload_complete_add_record_to_dynamodb(
        repo_under_test, set_env, mock_uuid
):
    repo_under_test.report_upload_complete(TEST_STAGING_METADATA)

    assert repo_under_test.dynamo_repository.create_item.call_count == len(
        TEST_STAGING_METADATA.files
    )

    for file in TEST_STAGING_METADATA.files:
        expected_dynamo_db_record = {
            "Date": "2023-10-01",
            "FilePath": file.file_path,
            "ID": mock_uuid,
            "NhsNumber": TEST_STAGING_METADATA.nhs_number,
            "Timestamp": 1696165200,
            "UploadStatus": "complete",
        }
        repo_under_test.dynamo_repository.create_item.assert_any_call(
            item=expected_dynamo_db_record, table_name=MOCK_BULK_REPORT_TABLE_NAME
        )


@freeze_time("2023-10-2 13:00:00")
def test_report_upload_failure_add_record_to_dynamodb(
        repo_under_test, set_env, mock_uuid
):
    mock_failure_reason = "File name invalid"
    repo_under_test.report_upload_failure(
        TEST_STAGING_METADATA, failure_reason=mock_failure_reason
    )

    for file in TEST_STAGING_METADATA.files:
        expected_dynamo_db_record = {
            "Date": "2023-10-02",
            "FilePath": file.file_path,
            "ID": mock_uuid,
            "NhsNumber": TEST_STAGING_METADATA.nhs_number,
            "Timestamp": 1696251600,
            "UploadStatus": "failed",
            "FailureReason": mock_failure_reason,
        }
        repo_under_test.dynamo_repository.create_item.assert_any_call(
            item=expected_dynamo_db_record, table_name=MOCK_BULK_REPORT_TABLE_NAME
        )


def test_rollback_transaction(repo_under_test, set_env, mock_uuid):
    repo_under_test.dynamo_records_in_transaction = TEST_DOCUMENT_REFERENCE_LIST
    repo_under_test.dest_bucket_files_in_transaction = [
        f"{TEST_NHS_NUMBER_FOR_BULK_UPLOAD}/mock_uuid_1",
        f"{TEST_NHS_NUMBER_FOR_BULK_UPLOAD}/mock_uuid_2",
    ]

    repo_under_test.rollback_transaction()

    repo_under_test.dynamo_repository.delete_item.assert_called_with(
        table_name=MOCK_LG_TABLE_NAME, key={"ID": mock_uuid}
    )
    assert repo_under_test.dynamo_repository.delete_item.call_count == len(
        TEST_DOCUMENT_REFERENCE_LIST
    )
