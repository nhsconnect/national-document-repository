import pytest
from handlers.bulk_upload_handler import lambda_handler
from tests.unit.helpers.data.bulk_upload.test_data import \
    TEST_EVENT_WITH_SQS_MESSAGES
from utils.lloyd_george_validator import LGInvalidFilesException


@pytest.fixture
def mocked_service(mocker):
    mocked_class = mocker.patch("handlers.bulk_upload_handler.BulkUploadService")
    mocked_service = mocked_class.return_value
    yield mocked_service


def test_lambda_process_each_sqs_message_one_by_one(set_env, mocked_service):
    lambda_handler(TEST_EVENT_WITH_SQS_MESSAGES, None)

    assert mocked_service.handle_sqs_message.call_count == len(
        TEST_EVENT_WITH_SQS_MESSAGES["Records"]
    )
    for message in TEST_EVENT_WITH_SQS_MESSAGES["Records"]:
        mocked_service.handle_sqs_message.assert_any_call(message)


def test_lambda_continue_process_next_message_after_handled_validation_error(
    set_env, mocked_service
):
    # emulate that validation error happen at 2nd message
    mocked_service.handle_sqs_message.side_effect = [
        None,
        LGInvalidFilesException,
        None,
    ]

    lambda_handler(TEST_EVENT_WITH_SQS_MESSAGES, None)

    mocked_service.handle_sqs_message.assert_called_with(
        TEST_EVENT_WITH_SQS_MESSAGES["Records"][2]
    )
