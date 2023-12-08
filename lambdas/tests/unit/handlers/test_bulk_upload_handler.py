import pytest
from handlers.bulk_upload_handler import lambda_handler
from tests.unit.helpers.data.bulk_upload.test_data import (
    TEST_EVENT_WITH_10_SQS_MESSAGES,
    TEST_EVENT_WITH_SQS_MESSAGES,
)
from utils.exceptions import InvalidMessageException, PdsTooManyRequestsException


@pytest.fixture
def mocked_service(mocker):
    mocked_class = mocker.patch("handlers.bulk_upload_handler.BulkUploadService")
    mocked_service = mocked_class.return_value
    yield mocked_service


def test_lambda_handler_process_each_sqs_message_one_by_one(
    set_env, mocked_service, context
):
    lambda_handler(TEST_EVENT_WITH_SQS_MESSAGES, context)

    assert mocked_service.handle_sqs_message.call_count == len(
        TEST_EVENT_WITH_SQS_MESSAGES["Records"]
    )
    for message in TEST_EVENT_WITH_SQS_MESSAGES["Records"]:
        mocked_service.handle_sqs_message.assert_any_call(message)


def test_lambda_handler_continue_process_next_message_after_handled_error(
    set_env, mocked_service, context
):
    # emulate that unexpected error happen at 2nd message
    mocked_service.handle_sqs_message.side_effect = [
        None,
        InvalidMessageException,
        None,
    ]

    lambda_handler(TEST_EVENT_WITH_SQS_MESSAGES, context)

    mocked_service.handle_sqs_message.assert_called_with(
        TEST_EVENT_WITH_SQS_MESSAGES["Records"][2]
    )


def test_lambda_handler_handle_pds_too_many_requests_exception(
    set_env, mocked_service, context
):
    # emulate that unexpected error happen at 7th message
    mocked_service.handle_sqs_message.side_effect = (
        [None] * 6 + [PdsTooManyRequestsException] + [None] * 3
    )
    expected_handled_messages = TEST_EVENT_WITH_10_SQS_MESSAGES["Records"][0:6]
    expected_unhandled_message = TEST_EVENT_WITH_10_SQS_MESSAGES["Records"][6:]

    lambda_handler(TEST_EVENT_WITH_10_SQS_MESSAGES, context)

    assert mocked_service.handle_sqs_message.call_count == 7

    for message in expected_handled_messages:
        mocked_service.handle_sqs_message.assert_any_call(message)

    for message in expected_unhandled_message:
        mocked_service.put_sqs_message_back_to_queue.assert_any_call(message)
