from datetime import datetime
from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError
from enums.patient_ods_inactive_status import PatientOdsInactiveStatus
from freezegun import freeze_time
from models.document_reference import DocumentReference
from models.sqs.mns_sqs_message import MNSSQSMessage
from services.process_mns_message_service import MNSNotificationService
from tests.unit.conftest import TEST_CURRENT_GP_ODS, TEST_NHS_NUMBER
from tests.unit.handlers.test_mns_notification_handler import (
    MOCK_DEATH_MESSAGE_BODY,
    MOCK_GP_CHANGE_MESSAGE_BODY,
    MOCK_INFORMAL_DEATH_MESSAGE_BODY,
    MOCK_REMOVED_DEATH_MESSAGE_BODY,
)
from utils.exceptions import PdsErrorException


@pytest.fixture
def mns_service(mocker, set_env, monkeypatch):
    monkeypatch.setenv("PDS_FHIR_IS_STUBBED", "False")
    service = MNSNotificationService()
    mocker.patch.object(service, "pds_service")
    mocker.patch.object(service, "document_service")
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
    yield service


@pytest.fixture
def mock_document_references(mocker):
    # Create a list of mock document references
    docs = []
    for i in range(3):
        doc = MagicMock(spec=DocumentReference)
        doc.id = f"doc-id-{i}"
        doc.nhs_number = TEST_NHS_NUMBER
        doc.current_gp_ods = TEST_CURRENT_GP_ODS
        doc.custodian = TEST_CURRENT_GP_ODS
        docs.append(doc)
    return docs


MOCK_UPDATE_TIME = "2024-01-01 12:00:00"
NEW_ODS_CODE = "NEW123"

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


def test_handle_mns_notification_error_handling_pds_error(mns_service, mocker):
    mocker.patch.object(
        mns_service,
        "handle_gp_change_notification",
        side_effect=PdsErrorException("PDS error"),
    )

    with pytest.raises(PdsErrorException):
        mns_service.handle_mns_notification(gp_change_message)


def test_handle_mns_notification_error_handling_client_error(mns_service, mocker):
    client_error = ClientError(
        {"Error": {"Code": "TestException", "Message": "Test exception"}}, "operation"
    )
    mocker.patch.object(
        mns_service, "handle_gp_change_notification", side_effect=client_error
    )

    with pytest.raises(ClientError):
        mns_service.handle_mns_notification(gp_change_message)


def test_handle_gp_change_notification_with_patient_documents(
    mns_service, mock_document_references, mocker
):
    mocker.patch.object(mns_service, "get_patient_documents")
    mns_service.get_patient_documents.return_value = mock_document_references
    mocker.patch.object(mns_service, "get_updated_gp_ods")
    mns_service.get_updated_gp_ods.return_value = NEW_ODS_CODE
    mocker.patch.object(mns_service, "update_patient_ods_code")

    mns_service.handle_gp_change_notification(gp_change_message)

    mns_service.get_patient_documents.assert_called_once_with(
        gp_change_message.subject.nhs_number
    )
    mns_service.get_updated_gp_ods.assert_called_once_with(
        gp_change_message.subject.nhs_number
    )
    mns_service.update_patient_ods_code.assert_called_once_with(
        mock_document_references, NEW_ODS_CODE
    )


def test_handle_gp_change_notification_no_patient_documents(mns_service, mocker):
    mocker.patch.object(mns_service, "get_patient_documents")
    mns_service.get_patient_documents.return_value = []
    mocker.patch.object(mns_service, "get_updated_gp_ods")
    mocker.patch.object(mns_service, "update_patient_ods_code")

    mns_service.get_patient_documents.return_value = []

    mns_service.handle_gp_change_notification(gp_change_message)

    mns_service.get_patient_documents.assert_called_once_with(
        gp_change_message.subject.nhs_number
    )
    mns_service.get_updated_gp_ods.assert_not_called()
    mns_service.update_patient_ods_code.assert_not_called()


def test_handle_death_notification_informal(mns_service, mocker):
    mocker.patch.object(mns_service, "get_patient_documents")
    mocker.patch.object(mns_service, "get_updated_gp_ods")
    mocker.patch.object(mns_service, "update_patient_ods_code")

    mns_service.handle_death_notification(informal_death_notification_message)

    mns_service.get_patient_documents.assert_not_called()
    mns_service.get_updated_gp_ods.assert_not_called()
    mns_service.update_patient_ods_code.assert_not_called()


def test_handle_death_notification_removed_with_documents(
    mns_service, mock_document_references, mocker
):
    mocker.patch.object(mns_service, "get_patient_documents")
    mocker.patch.object(mns_service, "get_updated_gp_ods")
    mocker.patch.object(mns_service, "update_patient_ods_code")
    mns_service.get_patient_documents.return_value = mock_document_references
    mns_service.get_updated_gp_ods.return_value = NEW_ODS_CODE

    mns_service.handle_death_notification(removed_death_notification_message)

    mns_service.get_patient_documents.assert_called_once_with(
        removed_death_notification_message.subject.nhs_number
    )
    mns_service.get_updated_gp_ods.assert_called_once_with(
        removed_death_notification_message.subject.nhs_number
    )
    mns_service.update_patient_ods_code.assert_called_once_with(
        mock_document_references, NEW_ODS_CODE
    )


def test_handle_death_notification_removed_no_documents(mns_service, mocker):
    mocker.patch.object(mns_service, "get_patient_documents")
    mocker.patch.object(mns_service, "get_updated_gp_ods")
    mocker.patch.object(mns_service, "update_patient_ods_code")
    mns_service.get_patient_documents.return_value = []

    mns_service.handle_death_notification(removed_death_notification_message)

    mns_service.get_patient_documents.assert_called_once_with(
        removed_death_notification_message.subject.nhs_number
    )
    mns_service.get_updated_gp_ods.assert_not_called()
    mns_service.update_patient_ods_code.assert_not_called()


def test_handle_death_notification_formal_with_documents(
    mns_service, mock_document_references, mocker
):
    mocker.patch.object(mns_service, "get_patient_documents")
    mocker.patch.object(mns_service, "get_updated_gp_ods")
    mocker.patch.object(mns_service, "update_patient_ods_code")
    mns_service.get_patient_documents.return_value = mock_document_references

    mns_service.handle_death_notification(death_notification_message)

    mns_service.get_patient_documents.assert_called_once_with(
        death_notification_message.subject.nhs_number
    )
    mns_service.update_patient_ods_code.assert_called_once_with(
        mock_document_references, PatientOdsInactiveStatus.DECEASED
    )
    mns_service.get_updated_gp_ods.assert_not_called()


def test_handle_death_notification_formal_no_documents(mns_service, mocker):
    mocker.patch.object(mns_service, "get_patient_documents")
    mocker.patch.object(mns_service, "get_updated_gp_ods")
    mocker.patch.object(mns_service, "update_patient_ods_code")
    mns_service.get_patient_documents.return_value = []

    mns_service.handle_death_notification(death_notification_message)

    mns_service.get_patient_documents.assert_called_once_with(
        death_notification_message.subject.nhs_number
    )
    mns_service.update_patient_ods_code.assert_not_called()


@freeze_time(MOCK_UPDATE_TIME)
def test_update_patient_ods_code_with_documents(mns_service, mock_document_references):
    updated_ods_code = NEW_ODS_CODE

    mns_service.update_patient_ods_code(mock_document_references, updated_ods_code)

    for doc in mock_document_references:
        assert doc.current_gp_ods == updated_ods_code
        assert doc.custodian == updated_ods_code
        assert doc.last_updated == int(
            datetime.fromisoformat(MOCK_UPDATE_TIME).timestamp()
        )

        mns_service.document_service.update_document.assert_any_call(
            mns_service.table,
            doc,
            mns_service.DOCUMENT_UPDATE_FIELDS,
        )


@freeze_time(MOCK_UPDATE_TIME)
def test_update_patient_ods_code_with_deceased_status(
    mns_service, mock_document_references
):
    mns_service.update_patient_ods_code(
        mock_document_references, PatientOdsInactiveStatus.DECEASED
    )

    for doc in mock_document_references:
        assert doc.current_gp_ods == PatientOdsInactiveStatus.DECEASED
        assert doc.custodian == mns_service.PCSE_ODS
        assert doc.last_updated == int(
            datetime.fromisoformat(MOCK_UPDATE_TIME).timestamp()
        )

        mns_service.document_service.update_document.assert_any_call(
            mns_service.table,
            doc,
            mns_service.DOCUMENT_UPDATE_FIELDS,
        )


@freeze_time(MOCK_UPDATE_TIME)
def test_update_patient_ods_code_with_suspended_status(
    mns_service, mock_document_references
):
    mns_service.update_patient_ods_code(
        mock_document_references, PatientOdsInactiveStatus.SUSPENDED
    )

    for doc in mock_document_references:
        assert doc.current_gp_ods == PatientOdsInactiveStatus.SUSPENDED
        assert doc.custodian == mns_service.PCSE_ODS
        assert doc.last_updated == int(
            datetime.fromisoformat(MOCK_UPDATE_TIME).timestamp()
        )

        mns_service.document_service.update_document.assert_any_call(
            mns_service.table,
            doc,
            mns_service.DOCUMENT_UPDATE_FIELDS,
        )


def test_update_patient_ods_code_no_documents(mns_service):
    mns_service.update_patient_ods_code([], NEW_ODS_CODE)

    mns_service.document_service.update_document.assert_not_called()


@freeze_time(MOCK_UPDATE_TIME)
def test_update_patient_ods_code_no_changes_needed(
    mns_service, mock_document_references
):
    for doc in mock_document_references:
        doc.current_gp_ods = NEW_ODS_CODE
        doc.custodian = NEW_ODS_CODE

    mns_service.update_patient_ods_code(mock_document_references, NEW_ODS_CODE)

    mns_service.document_service.update_document.assert_not_called()


def test_get_patient_documents(mns_service):
    expected_documents = [MagicMock(spec=DocumentReference)]
    mns_service.document_service.fetch_documents_from_table_with_nhs_number.return_value = (
        expected_documents
    )

    result = mns_service.get_patient_documents(TEST_NHS_NUMBER)

    assert result == expected_documents
    mns_service.document_service.fetch_documents_from_table_with_nhs_number.assert_called_once_with(
        TEST_NHS_NUMBER, mns_service.table
    )


def test_get_updated_gp_ods(mns_service):
    expected_ods = NEW_ODS_CODE
    patient_details_mock = MagicMock()
    patient_details_mock.general_practice_ods = expected_ods
    mns_service.pds_service.fetch_patient_details.return_value = patient_details_mock

    result = mns_service.get_updated_gp_ods(TEST_NHS_NUMBER)

    assert result == expected_ods
    mns_service.pds_service.fetch_patient_details.assert_called_once_with(
        TEST_NHS_NUMBER
    )


def test_pds_is_called_death_notification_removed(
    mns_service, mocker, mock_document_references
):
    mocker.patch.object(mns_service, "get_updated_gp_ods")
    mocker.patch.object(mns_service, "update_patient_ods_code")
    mocker.patch.object(mns_service, "get_patient_documents")

    mns_service.get_patient_documents.return_value = mock_document_references
    mns_service.handle_mns_notification(removed_death_notification_message)

    mns_service.get_updated_gp_ods.assert_called()
    mns_service.update_patient_ods_code.assert_called()
