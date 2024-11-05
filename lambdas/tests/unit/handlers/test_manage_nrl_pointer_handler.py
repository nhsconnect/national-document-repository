import json

import pytest
from handlers.manage_nrl_pointer_handler import lambda_handler


@pytest.fixture
def mock_service(mocker):
    mocked_class = mocker.patch("handlers.manage_nrl_pointer_handler.NrlApiService")
    mocked_instance = mocked_class.return_value
    mocked_class.return_value.end_user_ods_code = "NRL"
    return mocked_instance


def build_test_sqs_message(action="POST"):
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
    event = {"Records": [build_test_sqs_message("POST")]}

    lambda_handler(event, context)

    mock_service.create_new_pointer.assert_called_once()


def test_process_update_event_with_one_message(mock_service, context, set_env):
    event = {"Records": [build_test_sqs_message("UPDATE")]}

    lambda_handler(event, context)

    mock_service.update_pointer.assert_called_once()


def test_process_delete_event_with_one_message(mock_service, context, set_env):
    event = {"Records": [build_test_sqs_message("DELETE")]}

    lambda_handler(event, context)

    mock_service.delete_pointer.assert_called_once()


def test_process_event_with_few_message(mock_service, context, set_env):
    event = {
        "Records": [build_test_sqs_message("POST"), build_test_sqs_message("DELETE")]
    }

    lambda_handler(event, context)

    mock_service.create_new_pointer.assert_called_once()
    mock_service.delete_pointer.assert_called_once()
