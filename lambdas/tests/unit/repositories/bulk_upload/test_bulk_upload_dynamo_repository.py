@freeze_time("2023-10-1 13:00:00")
def test_report_upload_complete_add_record_to_dynamodb(set_env, mocker, mock_uuid):
    service = BulkUploadService()
    service.dynamo_repository = mocker.MagicMock()

    service.report_upload_complete(TEST_STAGING_METADATA)

    assert service.dynamo_repository.create_item.call_count == len(
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
        service.dynamo_repository.report_upload_complete.assert_any_call(
            item=expected_dynamo_db_record, table_name=MOCK_BULK_REPORT_TABLE_NAME
        )

@freeze_time("2023-10-2 13:00:00")
def test_report_upload_failure_add_record_to_dynamodb(set_env, mocker, mock_uuid):
    service = BulkUploadService()
    service.dynamo_repository = mocker.MagicMock()

    mock_failure_reason = "File name invalid"
    service.report_upload_failure(
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
        service.dynamo_repository.create_item.assert_any_call(
            item=expected_dynamo_db_record, table_name=MOCK_BULK_REPORT_TABLE_NAME