def test_put_staging_metadata_back_to_queue_and_increases_retries(
        set_env, mocker, service_under_test
):
    mocker.patch("uuid.uuid4", return_value="123412342")

    TEST_STAGING_METADATA.retries = 2
    metadata_copy = copy.deepcopy(TEST_STAGING_METADATA)
    metadata_copy.retries = 3

    service_under_test.put_staging_metadata_back_to_queue(TEST_STAGING_METADATA)

    service_under_test.sqs_repository.send_message_with_nhs_number_attr_fifo.assert_called_with(
        group_id="back_to_queue_bulk_upload_123412342",
        queue_url=MOCK_LG_METADATA_SQS_QUEUE,
        message_body=metadata_copy.model_dump_json(by_alias=True),
        nhs_number=TEST_STAGING_METADATA.nhs_number,
    )

def test_put_sqs_message_back_to_queue(set_env, service_under_test):
    service_under_test.put_sqs_message_back_to_queue(TEST_SQS_MESSAGE)

    service_under_test.sqs_repository.send_message_with_nhs_number_attr_fifo.assert_called_with(
        queue_url=MOCK_LG_METADATA_SQS_QUEUE,
        message_body=TEST_SQS_MESSAGE["body"],
        nhs_number=TEST_NHS_NUMBER_FOR_BULK_UPLOAD,
    )