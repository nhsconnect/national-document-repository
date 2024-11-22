from unittest.mock import call

import pytest
from enums.patient_ods_inactive_status import PatientOdsInactiveStatus
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


def test_update_patient_details(mns_service):
    mns_service.update_patient_details(
        MOCK_SEARCH_RESPONSE["Items"], PatientOdsInactiveStatus.DECEASED.value
    )
    calls = [
        call(
            table_name=mns_service.table,
            key="3d8683b9-1665-40d2-8499-6e8302d507ff",
            updated_fields={"CurrentGpOds": PatientOdsInactiveStatus.DECEASED.value},
        ),
        call(
            table_name=mns_service.table,
            key="4d8683b9-1665-40d2-8499-6e8302d507ff",
            updated_fields={"CurrentGpOds": PatientOdsInactiveStatus.DECEASED.value},
        ),
        call(
            table_name=mns_service.table,
            key="5d8683b9-1665-40d2-8499-6e8302d507ff",
            updated_fields={"CurrentGpOds": PatientOdsInactiveStatus.DECEASED.value},
        ),
    ]
    mns_service.dynamo_service.update_item.assert_has_calls(calls, any_order=False)
