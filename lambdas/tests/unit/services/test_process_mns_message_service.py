import pytest
from models.mns_sqs_message import MNSSQSMessage
from services.process_mns_message_service import MNSNotificationService
from tests.unit.handlers.test_mns_notification_handler import (
    MOCK_DEATH_MESSAGE_BODY,
    MOCK_GP_CHANGE_MESSAGE_BODY,
)


@pytest.fixture
def mns_service(mocker):
    service = MNSNotificationService()
    mocker.patch.object(service, "handle_gp_change_notification")

    yield service


gp_change_message = MNSSQSMessage(**MOCK_GP_CHANGE_MESSAGE_BODY)
death_notification_message = MNSSQSMessage(**MOCK_DEATH_MESSAGE_BODY)


def test_handle_gp_change_message_called_message_type_GP_change(mns_service):

    mns_service.handle_mns_notification(gp_change_message)
    mns_service.handle_gp_change_notification.assert_called()


def test_handle_gp_change_message_not_called_message_death_message(mns_service):
    mns_service.handle_mns_notification(death_notification_message)
    mns_service.handle_gp_change_notification.assert_not_called()
