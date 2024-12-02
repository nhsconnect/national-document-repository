from datetime import datetime
from unittest.mock import call

import pytest
from enums.metadata_field_names import DocumentReferenceMetadataFields
from enums.patient_ods_inactive_status import PatientOdsInactiveStatus
from freezegun import freeze_time
from models.mns_sqs_message import MNSSQSMessage
from services.process_mns_message_service import MNSNotificationService
from tests.unit.conftest import TEST_CURRENT_GP_ODS
from tests.unit.handlers.test_mns_notification_handler import (
    MOCK_DEATH_MESSAGE_BODY,
    MOCK_GP_CHANGE_MESSAGE_BODY,
    MOCK_INFORMAL_DEATH_MESSAGE_BODY,
    MOCK_REMOVED_DEATH_MESSAGE_BODY,
)
from tests.unit.helpers.data.dynamo_responses import (
    MOCK_EMPTY_RESPONSE,
    MOCK_SEARCH_RESPONSE,
)
from utils.exceptions import PdsErrorException


@pytest.fixture
def mns_service(mocker, set_env, monkeypatch):
    monkeypatch.setenv("PDS_FHIR_IS_STUBBED", "False")
    service = MNSNotificationService()
    mocker.patch.object(service, "dynamo_service")
    mocker.patch.object(service, "get_updated_gp_ods")
    mocker.patch.object(service, "sqs_service")
    yield service


@pytest.fixture
def mock_handle_gp_change(mocker, mns_service):
    service = mns_service
    mocker.patch.object(service, "handle_gp_change_notification")
    yield service


@pytest.fixture
def mock_handle_death_notification(mocker, mns_service):
    service = mns_service
    mocker.patch.object(service, "handle_death_notification")


MOCK_UPDATE_TIME = "2024-01-01 12:00:00"

gp_change_message = MNSSQSMessage(**MOCK_GP_CHANGE_MESSAGE_BODY)
death_notification_message = MNSSQSMessage(**MOCK_DEATH_MESSAGE_BODY)
informal_death_notification_message = MNSSQSMessage(**MOCK_INFORMAL_DEATH_MESSAGE_BODY)
removed_death_notification_message = MNSSQSMessage(**MOCK_REMOVED_DEATH_MESSAGE_BODY)


def test_handle_gp_change_message_called_message_type_gp_change(
    mns_service, mock_handle_gp_change, mock_handle_death_notification
):
    mns_service.handle_mns_notification(gp_change_message)

    mns_service.handle_death_notification.assert_not_called()
    mns_service.handle_gp_change_notification.assert_called_with(gp_change_message)


def test_handle_gp_change_message_not_called_message_death_message(
    mns_service, mock_handle_death_notification, mock_handle_gp_change
):
    mns_service.handle_mns_notification(death_notification_message)

    mns_service.handle_gp_change_notification.assert_not_called()
    mns_service.handle_death_notification.assert_called_with(death_notification_message)


def test_has_patient_in_ndr_populate_response_from_dynamo(mns_service):
    response = MOCK_SEARCH_RESPONSE["Items"]
    assert mns_service.patient_is_present_in_ndr(response) is True


def test_has_patient_in_ndr_empty_dynamo_response(mns_service):
    response = MOCK_EMPTY_RESPONSE["Items"]
    assert mns_service.patient_is_present_in_ndr(response) is False


@pytest.mark.parametrize(
    "event_message, output",
    [
        (removed_death_notification_message, False),
        (informal_death_notification_message, True),
        (death_notification_message, False),
    ],
)
def test_is_informal_death_notification(mns_service, event_message, output):
    assert mns_service.is_informal_death_notification(event_message) is output


@pytest.mark.parametrize(
    "event_message, output",
    [
        (removed_death_notification_message, True),
        (informal_death_notification_message, False),
        (death_notification_message, False),
    ],
)
def test_is_removed_death_notification(mns_service, event_message, output):
    assert mns_service.is_removed_death_notification(event_message) is output


@pytest.mark.parametrize(
    "event_message, output",
    [
        (removed_death_notification_message, False),
        (informal_death_notification_message, False),
        (death_notification_message, True),
    ],
)
def test_is_formal_death_notification(mns_service, event_message, output):
    assert mns_service.is_formal_death_notification(event_message) is output


def test_handle_notification_not_called_message_type_not_death_or_gp_notification(
    mns_service,
):
    mns_service.is_informal_death_notification(informal_death_notification_message)
    mns_service.get_updated_gp_ods.assert_not_called()


def test_pds_is_called_death_notification_removed(mns_service, mocker):
    mocker.patch.object(mns_service, "update_patient_details")
    mns_service.dynamo_service.query_table_by_index.return_value = MOCK_SEARCH_RESPONSE
    mns_service.handle_mns_notification(removed_death_notification_message)

    mns_service.get_updated_gp_ods.assert_called()
    mns_service.update_patient_details.assert_called()


@freeze_time(MOCK_UPDATE_TIME)
def test_update_patient_details(mns_service):
    mns_service.update_patient_details(
        MOCK_SEARCH_RESPONSE["Items"], PatientOdsInactiveStatus.DECEASED
    )
    calls = [
        call(
            table_name=mns_service.table,
            key="3d8683b9-1665-40d2-8499-6e8302d507ff",
            updated_fields={
                DocumentReferenceMetadataFields.CURRENT_GP_ODS.value: PatientOdsInactiveStatus.DECEASED,
                DocumentReferenceMetadataFields.LAST_UPDATED.value: int(
                    datetime.fromisoformat(MOCK_UPDATE_TIME).timestamp()
                ),
            },
        ),
        call(
            table_name=mns_service.table,
            key="4d8683b9-1665-40d2-8499-6e8302d507ff",
            updated_fields={
                DocumentReferenceMetadataFields.CURRENT_GP_ODS.value: PatientOdsInactiveStatus.DECEASED,
                DocumentReferenceMetadataFields.LAST_UPDATED.value: int(
                    datetime.fromisoformat(MOCK_UPDATE_TIME).timestamp()
                ),
            },
        ),
        call(
            table_name=mns_service.table,
            key="5d8683b9-1665-40d2-8499-6e8302d507ff",
            updated_fields={
                DocumentReferenceMetadataFields.CURRENT_GP_ODS.value: PatientOdsInactiveStatus.DECEASED,
                DocumentReferenceMetadataFields.LAST_UPDATED.value: int(
                    datetime.fromisoformat(MOCK_UPDATE_TIME).timestamp()
                ),
            },
        ),
    ]
    mns_service.dynamo_service.update_item.assert_has_calls(calls, any_order=False)


def test_update_gp_ods_not_called_empty_dynamo_response(mns_service):
    mns_service.dynamo_service.query_table_by_index.return_value = MOCK_EMPTY_RESPONSE
    mns_service.handle_gp_change_notification(gp_change_message)

    mns_service.get_updated_gp_ods.assert_not_called()


def test_update_gp_ods_called_dynamo_response(mns_service):
    mns_service.dynamo_service.query_table_by_index.return_value = MOCK_SEARCH_RESPONSE
    mns_service.handle_gp_change_notification(gp_change_message)

    mns_service.get_updated_gp_ods.assert_called()


def test_update_gp_ods_not_called_ods_codes_are_the_same(mns_service):
    mns_service.dynamo_service.query_table_by_index.return_value = MOCK_SEARCH_RESPONSE
    mns_service.get_updated_gp_ods.return_value = TEST_CURRENT_GP_ODS
    mns_service.handle_gp_change_notification(gp_change_message)

    mns_service.dynamo_service.update_item.assert_not_called()


@freeze_time(MOCK_UPDATE_TIME)
def test_handle_gp_change_updates_gp_ods_code(mns_service):
    mns_service.dynamo_service.query_table_by_index.return_value = MOCK_SEARCH_RESPONSE
    other_gp_ods = "Z12345"
    mns_service.get_updated_gp_ods.return_value = other_gp_ods
    mns_service.handle_gp_change_notification(gp_change_message)

    calls = [
        call(
            table_name=mns_service.table,
            key="3d8683b9-1665-40d2-8499-6e8302d507ff",
            updated_fields={
                DocumentReferenceMetadataFields.CURRENT_GP_ODS.value: other_gp_ods,
                DocumentReferenceMetadataFields.LAST_UPDATED.value: int(
                    datetime.fromisoformat(MOCK_UPDATE_TIME).timestamp()
                ),
            },
        ),
        call(
            table_name=mns_service.table,
            key="4d8683b9-1665-40d2-8499-6e8302d507ff",
            updated_fields={
                DocumentReferenceMetadataFields.CURRENT_GP_ODS.value: other_gp_ods,
                DocumentReferenceMetadataFields.LAST_UPDATED.value: int(
                    datetime.fromisoformat(MOCK_UPDATE_TIME).timestamp()
                ),
            },
        ),
        call(
            table_name=mns_service.table,
            key="5d8683b9-1665-40d2-8499-6e8302d507ff",
            updated_fields={
                DocumentReferenceMetadataFields.CURRENT_GP_ODS.value: other_gp_ods,
                DocumentReferenceMetadataFields.LAST_UPDATED.value: int(
                    datetime.fromisoformat(MOCK_UPDATE_TIME).timestamp()
                ),
            },
        ),
    ]
    mns_service.dynamo_service.update_item.assert_has_calls(calls, any_order=False)


def test_messages_is_put_back_on_the_queue_when_pds_error_raised(
    mns_service, mocker, mock_handle_gp_change
):
    mns_service.handle_gp_change_notification.side_effect = PdsErrorException()
    mocker.patch.object(mns_service, "send_message_back_to_queue")
    mns_service.handle_mns_notification(gp_change_message)

    mns_service.send_message_back_to_queue.assert_called_with(gp_change_message)
