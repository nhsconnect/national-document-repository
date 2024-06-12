import copy

import pytest
from repositories.bulk_upload.bulk_upload_sqs_repository import BulkUploadSqsRepository
from tests.unit.conftest import MOCK_LG_METADATA_SQS_QUEUE
from tests.unit.helpers.data.bulk_upload.test_data import (
    TEST_NHS_NUMBER_FOR_BULK_UPLOAD,
    TEST_SQS_MESSAGE,
    TEST_STAGING_METADATA,
)


@pytest.fixture
def repo_under_test(mocker, set_env):
    repo = BulkUploadSqsRepository()
    mocker.patch.object(repo, "sqs_repository")
    yield repo


def test_put_staging_metadata_back_to_queue_and_increases_retries(
    set_env, mock_uuid, repo_under_test
):
    TEST_STAGING_METADATA.retries = 2
    metadata_copy = copy.deepcopy(TEST_STAGING_METADATA)
    metadata_copy.retries = 3

    repo_under_test.put_staging_metadata_back_to_queue(TEST_STAGING_METADATA)

    repo_under_test.sqs_repository.send_message_with_nhs_number_attr_fifo.assert_called_with(
        group_id=f"back_to_queue_bulk_upload_{mock_uuid}",
        queue_url=MOCK_LG_METADATA_SQS_QUEUE,
        message_body=metadata_copy.model_dump_json(by_alias=True),
        nhs_number=TEST_STAGING_METADATA.nhs_number,
    )


def test_put_sqs_message_back_to_queue(set_env, repo_under_test):
    repo_under_test.put_sqs_message_back_to_queue(TEST_SQS_MESSAGE)

    repo_under_test.sqs_repository.send_message_with_nhs_number_attr_fifo.assert_called_with(
        queue_url=MOCK_LG_METADATA_SQS_QUEUE,
        message_body=TEST_SQS_MESSAGE["body"],
        nhs_number=TEST_NHS_NUMBER_FOR_BULK_UPLOAD,
    )
