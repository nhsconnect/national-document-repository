import json
from unittest.mock import ANY

import pytest
from handlers.bulk_upload_handler import handle_invalid_message, lambda_handler
from services.lloyd_george_validator import LGInvalidFilesException
from tests.unit.conftest import MOCK_LG_INVALID_SQS_QUEUE
from tests.unit.helpers.data.bulk_upload.test_data import (
    TEST_EVENT_WITH_SQS_MESSAGES, TEST_NHS_NUMBER_FOR_BULK_UPLOAD)


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


def test_lambda_calls_handle_invalid_message_when_validation_failed(
    set_env, mocker, mocked_service
):
    # emulate that validation error happen at 2nd message
    mocked_service.handle_sqs_message.side_effect = [
        None,
        LGInvalidFilesException,
        None,
    ]
    mocked_handle_invalid_message = mocker.patch(
        "handlers.bulk_upload_handler.handle_invalid_message"
    )

    lambda_handler(TEST_EVENT_WITH_SQS_MESSAGES, None)

    mocked_handle_invalid_message.assert_called_once_with(
        invalid_message=TEST_EVENT_WITH_SQS_MESSAGES["Records"][1], error=ANY
    )


def test_lambda_continue_process_next_message_after_handled_validation_error(
    set_env, mocker, mocked_service
):
    # emulate that validation error happen at 2nd message
    mocked_service.handle_sqs_message.side_effect = [
        None,
        LGInvalidFilesException,
        None,
    ]
    mocker.patch("handlers.bulk_upload_handler.handle_invalid_message")

    lambda_handler(TEST_EVENT_WITH_SQS_MESSAGES, None)

    mocked_service.handle_sqs_message.assert_called_with(
        TEST_EVENT_WITH_SQS_MESSAGES["Records"][2]
    )


def test_handle_invalid_message(
    set_env,
    mocker,
):
    mocked_sqs_service = mocker.patch(
        "handlers.bulk_upload_handler.SQSService"
    ).return_value

    handle_invalid_message(
        TEST_EVENT_WITH_SQS_MESSAGES["Records"][0],
        error=LGInvalidFilesException("filename incorrect"),
    )

    expected_message_body = {
        "original_message": TEST_EVENT_WITH_SQS_MESSAGES["Records"][0]["body"],
        "error": str(LGInvalidFilesException("filename incorrect")),
    }

    mocked_sqs_service.send_message_with_nhs_number_attr.assert_called_with(
        queue_url=MOCK_LG_INVALID_SQS_QUEUE,
        message_body=json.dumps(expected_message_body),
        nhs_number=TEST_NHS_NUMBER_FOR_BULK_UPLOAD,
    )
