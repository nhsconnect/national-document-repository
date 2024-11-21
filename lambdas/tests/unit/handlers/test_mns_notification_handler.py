import json

from enums.mns_notification_types import MNSNotificationTypes
from handlers.mns_notification_handler import lambda_handler
from unit.conftest import FAKE_URL, TEST_NHS_NUMBER, TEST_UUID
from unit.services.base.test_cloudwatch_logs_query_service import MOCK_START_TIME

MOCK_GP_CHANGE_MESSAGE_BODY = {
    "id": TEST_UUID,
    "type": MNSNotificationTypes.CHANGE_OF_GP.value,
    "subject": {
        "nhs_number": TEST_NHS_NUMBER,
        "family_name": "SMITH",
        "dob": "2010-10-22",
    },
    "source": {
        "name": FAKE_URL,
        "identifiers": {
            "system": FAKE_URL,
            "value": TEST_UUID,
        },
    },
    "time": f"{MOCK_START_TIME}",
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


def test_handler(context, set_env):

    event = {"Records": [{"body": json.dumps(MOCK_GP_CHANGE_MESSAGE_BODY)}]}

    assert lambda_handler(event, context) == TEST_NHS_NUMBER
