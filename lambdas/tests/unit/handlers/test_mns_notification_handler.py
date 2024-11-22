import json
from copy import deepcopy

import pytest
from enums.mns_notification_types import MNSNotificationTypes
from handlers.mns_notification_handler import lambda_handler
from tests.unit.conftest import FAKE_URL, TEST_NHS_NUMBER, TEST_UUID

MOCK_DATE = "2010-10-22"

MOCK_GP_CHANGE_MESSAGE_BODY = {
    "id": TEST_UUID,
    "type": MNSNotificationTypes.CHANGE_OF_GP.value,
    "subject": {
        "nhs_number": TEST_NHS_NUMBER,
        "family_name": "SMITH",
        "dob": MOCK_DATE,
    },
    "source": {
        "name": FAKE_URL,
        "identifiers": {
            "system": FAKE_URL,
            "value": TEST_UUID,
        },
    },
    "time": MOCK_DATE,
    "data": {
        "full_url": FAKE_URL,
        "version_id": TEST_UUID,
        "provenance": {
            "name": "Fake GP",
            "identifiers": {
                "system": FAKE_URL,
                "value": TEST_UUID,
            },
        },
        "registrationEncounterCode": "00",
    },
}

MOCK_DEATH_MESSAGE_BODY = deepcopy(MOCK_GP_CHANGE_MESSAGE_BODY)
MOCK_DEATH_MESSAGE_BODY["type"] = MNSNotificationTypes.DEATH_NOTIFICATION.value

MOCK_OTHER_NOTIFICATION_MESSAGE_BODY = deepcopy(MOCK_GP_CHANGE_MESSAGE_BODY)
MOCK_OTHER_NOTIFICATION_MESSAGE_BODY["type"] = "imms-vaccinations-1"


@pytest.fixture
def mock_service(mocker):
    mocked_class = mocker.patch(
        "handlers.mns_notification_handler.MNSNotificationService"
    )
    mocked_instance = mocked_class.return_value
    return mocked_instance


def test_handle_notification_called_message_type_GP_change(
    context, set_env, mock_service
):

    event = {"Records": [{"body": json.dumps(MOCK_GP_CHANGE_MESSAGE_BODY)}]}
    lambda_handler(event, context)

    mock_service.handle_mns_notification.assert_called()


def test_handle_notification_called_message_type_death_notification(
    context, set_env, mock_service
):
    pass


def test_handle_notification_not_called_message_type_not_death_or_GP_notification(
    context, set_env, mock_service
):

    event = {"Records": [{"body": json.dumps(MOCK_OTHER_NOTIFICATION_MESSAGE_BODY)}]}
    lambda_handler(event, context)

    mock_service.handle_mns_notification.assert_not_called()


def test_handle_notification_not_called_no_records_in_event(
    context, set_env, mock_service
):
    event = {"Records": []}
    lambda_handler(event, context)

    mock_service.handle_mns_notification.assert_not_called()
