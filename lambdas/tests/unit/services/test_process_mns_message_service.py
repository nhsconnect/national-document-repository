import pytest
from models.mns_sqs_message import MNSSQSMessage
from services.process_mns_message_service import MNSNotificationService
from tests.unit.handlers.test_mns_notification_handler import (
    MOCK_DEATH_MESSAGE_BODY,
    MOCK_GP_CHANGE_MESSAGE_BODY,
    MOCK_INFORMAL_DEATH_MESSAGE_BODY,
)
from tests.unit.helpers.data.dynamo_responses import MOCK_SEARCH_RESPONSE


@pytest.fixture
def mns_service(mocker, set_env):
    service = MNSNotificationService()
    mocker.patch.object(service, "handle_gp_change_notification")
    mocker.patch.object(service, "dynamo_service")

    yield service


@pytest.fixture
def mock_dynamo_service(mns_service, mocker):
    mock_dynamo_service = mns_service.dynamo_service
    mocker.patch.object(mock_dynamo_service, "update_item")
    mocker.patch.object(mock_dynamo_service, "query_table_by_index")
    yield mock_dynamo_service


gp_change_message = MNSSQSMessage(**MOCK_GP_CHANGE_MESSAGE_BODY)
death_notification_message = MNSSQSMessage(**MOCK_DEATH_MESSAGE_BODY)
informal_death_notification_message = MNSSQSMessage(**MOCK_INFORMAL_DEATH_MESSAGE_BODY)


def test_handle_gp_change_message_called_message_type_GP_change(mns_service):

    mns_service.handle_mns_notification(gp_change_message)
    mns_service.handle_gp_change_notification.assert_called()


def test_handle_gp_change_message_not_called_message_death_message(mns_service):
    mns_service.handle_mns_notification(death_notification_message)
    mns_service.handle_gp_change_notification.assert_not_called()


def test_is_informal_death_notification(mns_service):
    assert (
        mns_service.is_informal_death_notification(death_notification_message) is True
    )
    assert (
        mns_service.is_informal_death_notification(informal_death_notification_message)
        is False
    )


def test_have_patient_in_table(mns_service):
    result = mns_service.have_patient_in_table(gp_change_message)
    mns_service.dynamo_service.query_table_by_index.assert_called()
    mns_service.dynamo_service.return_value.query_table_by_index.return_value = (
        MOCK_SEARCH_RESPONSE
    )

    assert result is True
