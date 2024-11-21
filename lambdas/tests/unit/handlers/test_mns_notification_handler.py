from enums.mns_notification_types import MNSNotificationTypes
from unit.conftest import FAKE_URL, TEST_NHS_NUMBER, TEST_UUID
from unit.services.base.test_cloudwatch_logs_query_service import MOCK_START_TIME

MOCK_GP_CHANGE_MESSAGE_BODY = {
    "id": TEST_UUID,
    "type": MNSNotificationTypes.CHANGE_OF_GP,
    "subject": {
        "nhsNumber": TEST_NHS_NUMBER,
        "familyName": "SMITH",
        "dob": "2010-10-22",
    },
    "source": {
        "name": FAKE_URL,
        "identifiers": {
            "system": FAKE_URL,
            "value": TEST_UUID,
        },
    },
    "time": MOCK_START_TIME,
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
