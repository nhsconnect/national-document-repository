import json

import pytest
from handlers.manage_nrl_pointer_handler import lambda_handler
from utils.exceptions import NrlApiException


@pytest.fixture
def mock_service(mocker):
    mocked_class = mocker.patch("handlers.manage_nrl_pointer_handler.NrlApiService")
    mocked_instance = mocked_class.return_value
    mocked_class.return_value.end_user_ods_code = "NRL"
    return mocked_instance


def build_test_sqs_message(action="create"):
    SQS_Message = {
        "nhs_number": "123456789",
        "snomed_code_doc_type": "16521000000101",
        "snomed_code_category": "734163000",
        "action": action,
        "attachment": {
            "contentType": "application/pdf",
            "url": "https://example.org/my-doc.pdf",
        },
    }
    return {
        "body": json.dumps(SQS_Message),
        "eventSource": "aws:sqs",
    }


def test_process_event_with_one_message(mock_service, context, set_env):
    event = {"Records": [build_test_sqs_message("create")]}

    lambda_handler(event, context)

    mock_service.create_new_pointer.assert_called_once()


def test_process_delete_event_with_one_message(mock_service, context, set_env):
    event = {"Records": [build_test_sqs_message("delete")]}

    lambda_handler(event, context)

    mock_service.delete_pointer.assert_called_once()


def test_process_event_with_multiple_messages(mock_service, context, set_env):
    event = {
        "Records": [build_test_sqs_message("create"), build_test_sqs_message("delete")]
    }

    lambda_handler(event, context)

    mock_service.create_new_pointer.assert_called_once()
    mock_service.delete_pointer.assert_called_once()


def test_failed_to_create_a_pointer(mock_service, context, set_env, caplog):
    event = {"Records": [build_test_sqs_message("create")]}
    mock_service.create_new_pointer.side_effect = NrlApiException("test exception")

    lambda_handler(event, context)

    expected_log = "Failed to process current message due to error: test exception"
    actual_log = caplog.records[-2].msg
    assert actual_log == expected_log
    mock_service.create_new_pointer.assert_called_once()
