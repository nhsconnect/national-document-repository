import json
from copy import deepcopy

import pytest
from enums.mns_notification_types import MNSNotificationTypes
from handlers.mns_notification_handler import lambda_handler
from tests.unit.conftest import FAKE_URL, TEST_NHS_NUMBER, TEST_UUID

MOCK_TIME = "2022-04-05T17:31:00.000Z"

MOCK_GP_CHANGE_MESSAGE_BODY = {
    "id": TEST_UUID,
    "type": MNSNotificationTypes.CHANGE_OF_GP.value,
    "subject": {
        "nhsNumber": TEST_NHS_NUMBER,
        "family_name": "SMITH",
        "dob": "2017-10-02",
    },
    "source": {
        "name": FAKE_URL,
        "identifiers": {
            "system": FAKE_URL,
            "value": TEST_UUID,
        },
    },
    "time": MOCK_TIME,
    "data": {
        "fullUrl": FAKE_URL,
        "versionId": TEST_UUID,
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

MOCK_DEATH_MESSAGE_BODY = {
    "id": TEST_UUID,
    "type": "pds-death-notification-1",
    "subject": {
        "dob": "2017-10-02",
        "familyName": "DAWKINS",
        "nhsNumber": TEST_NHS_NUMBER,
    },
    "source": {
        "name": "NHS DIGITAL",
        "identifier": {
            "system": "https://fhir.nhs.uk/Id/nhsSpineASID",
            "value": "477121000324",
        },
    },
    "time": MOCK_TIME,
    "data": {
        "versionId": 'W/"16"',
        "fullUrl": "https://int.api.service.nhs.uk/personal-demographics/FHIR/R4/Patient/9912003888",
        "deathNotificationStatus": "2",
        "provenance": {
            "name": "The GP Practice",
            "identifiers": {
                "system": "https://fhir.nhs.uk/Id/nhsSpineASID",
                "value": "477121000323",
            },
        },
    },
}

MOCK_OTHER_NOTIFICATION_MESSAGE_BODY = deepcopy(MOCK_GP_CHANGE_MESSAGE_BODY)
MOCK_OTHER_NOTIFICATION_MESSAGE_BODY["type"] = "imms-vaccinations-1"

MOCK_INFORMAL_DEATH_MESSAGE_BODY = deepcopy(MOCK_DEATH_MESSAGE_BODY)
MOCK_INFORMAL_DEATH_MESSAGE_BODY["data"]["deathNotificationStatus"] = "1"


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
    event = {"Records": [{"body": json.dumps(MOCK_DEATH_MESSAGE_BODY)}]}
    lambda_handler(event, context)

    mock_service.handle_mns_notification.assert_called()


def test_handle_notification_not_called_no_records_in_event(
    context, set_env, mock_service
):
    event = {"Records": []}
    lambda_handler(event, context)

    mock_service.handle_mns_notification.assert_not_called()
