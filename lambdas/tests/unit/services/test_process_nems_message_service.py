import pytest
from botocore.exceptions import ClientError
from enums.nems_error_types import NEMS_ERROR_TYPES
from fhir.resources.STU3.bundle import Bundle
from services.process_nems_message_service import ProcessNemsMessageService
from utils.exceptions import (
    FhirResourceNotFound,
    InvalidResourceIdException,
    OdsErrorException,
    OrganisationNotFoundException,
)


@pytest.fixture
def mock_service(mocker, set_env):
    service = ProcessNemsMessageService()
    mocker.patch.object(service, "ods_api_service")
    mocker.patch.object(service, "document_service")
    yield service


@pytest.fixture
def mock_fhir_bundle(mocker):
    mock_fhir_bundle = mocker.patch("fhir.resources.STU3.bundle.Bundle.parse_raw")
    yield mock_fhir_bundle


@pytest.fixture
def mock_map_bundle_entries_to_dict(mocker):
    mock_map_bundle_entries_to_dict = mocker.patch(
        "services.process_nems_message_service.map_bundle_entries_to_dict"
    )
    yield mock_map_bundle_entries_to_dict


@pytest.fixture
def mock_validate_id(mocker):
    mock_validate_id = mocker.patch("services.process_nems_message_service.validate_id")
    yield mock_validate_id


@pytest.fixture
def mock_validate_nems_details(mocker, mock_service):
    mock_validate_nems_details = mocker.MagicMock()
    mock_service.validate_nems_details = mock_validate_nems_details
    yield mock_validate_nems_details


@pytest.fixture
def mock_update_LG_table_with_current_GP(mocker, mock_service):
    mock_update_LG_table_with_current_GP = mocker.MagicMock()
    mock_service.update_LG_table_with_current_GP = mock_update_LG_table_with_current_GP
    yield mock_update_LG_table_with_current_GP


# Load Test Files
with open("tests/unit/data/sqs_messages/address_change_valid_message.xml") as f:
    _valid_non_change_of_gp_message = f.read()

with open("tests/unit/data/sqs_messages/invalid_message_with_no_header.xml") as f:
    _message_with_no_header = f.read()

with open("tests/unit/data/sqs_messages/gp_change_valid_message.xml") as f:
    _valid_change_of_gp_message = f.read()

non_change_of_gp_bundle = Bundle.parse_raw(
    _valid_non_change_of_gp_message, content_type="text/xml"
)
valid_bundle = Bundle.parse_raw(_valid_change_of_gp_message, content_type="text/xml")
change_of_gp_message_header = valid_bundle.entry[0]
patient_bundle_resource = valid_bundle.entry[3]
active_gp_organisation = valid_bundle.entry[4]
previous_gp_organisation = valid_bundle.entry[6]
organisation_bundle_resources = [active_gp_organisation, previous_gp_organisation]


def test_process_messages_from_event_empty_records_return_empty_list(
    mocker, mock_service
):
    records = []
    mock_service.handle_message = mocker.MagicMock()

    response = mock_service.process_messages_from_event(records)

    assert response == []
    mock_service.handle_message.assert_not_called()


def test_process_messages_from_event_handle_happy_path_return_empty_list(
    mocker, mock_service
):
    records = [{"messageId": "test1"}, {"messageId": "test2"}]
    mock_service.handle_message = mocker.MagicMock()
    mock_service.handle_message.return_value = None

    response = mock_service.process_messages_from_event(records)

    assert response == []
    assert mock_service.handle_message.call_count == 2


def test_process_messages_from_event_handle_happy_path_return_failures_list(
    mocker, mock_service
):
    records = [{"messageId": "test1"}, {"messageId": "test2"}]
    mock_service.handle_message = mocker.MagicMock()
    mock_service.handle_message.return_value = "test_value"

    response = mock_service.process_messages_from_event(records)

    assert response == [{"itemIdentifier": "test1"}, {"itemIdentifier": "test2"}]
    assert mock_service.handle_message.call_count == 2


def test_handle_message_when_message_has_no_message_attributes_returns_validation_error_type_response(
    mock_service,
):
    input_message = {}
    expected_response = NEMS_ERROR_TYPES.Validation

    response = mock_service.handle_message(input_message)

    assert response == expected_response


def test_handle_message_when_message_has_no_body_returns_validation_error_type_response(
    mock_service,
):
    input_message = {"messageAttributes": {}}
    expected_response = NEMS_ERROR_TYPES.Validation

    response = mock_service.handle_message(input_message)

    assert response == expected_response


def test_handle_message_when_message_is_not_xml_returns_validation_error_type_response(
    mock_service,
):
    input_message = {"body": "<>", "messageAttributes": {}, "messageId": "test-id"}
    expected_response = NEMS_ERROR_TYPES.Validation

    response = mock_service.handle_message(input_message)

    assert response == expected_response


def test_handle_message_when_message_is_not_fhir_compliant_returns_validation_error_type_response(
    mock_service, mock_fhir_bundle, validation_error
):
    input_message = {
        "body": "<test></test>",
        "messageAttributes": {},
        "messageId": "test-id",
    }
    expected_response = NEMS_ERROR_TYPES.Validation
    mock_fhir_bundle.side_effect = validation_error

    response = mock_service.handle_message(input_message)

    assert response == expected_response


def test_handle_message_when_message_does_not_contain_message_header_entry_returns_validation_error_type_response(
    mock_service, mock_map_bundle_entries_to_dict, mock_fhir_bundle
):
    input_message = {
        "body": _message_with_no_header,
        "messageAttributes": {},
        "messageId": "test-id",
    }
    expected_response = NEMS_ERROR_TYPES.Data
    mock_map_bundle_entries_to_dict.return_value = {}

    response = mock_service.handle_message(input_message)

    assert response == expected_response
    mock_map_bundle_entries_to_dict.assert_called_once()
    mock_fhir_bundle.assert_called_once()


def test_handle_message_returns_transient_error_when_handle_change_of_gp_message_raises_client_error(
    mocker, mock_service, mock_map_bundle_entries_to_dict, mock_fhir_bundle
):
    input_message = {
        "body": _valid_change_of_gp_message,
        "messageAttributes": {},
        "messageId": "test-id",
    }
    expected_response = NEMS_ERROR_TYPES.Transient
    mock_service.handle_change_of_gp_message = mocker.MagicMock()
    mock_service.handle_change_of_gp_message.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "mocked error"}}, "test"
    )
    mock_map_bundle_entries_to_dict.return_value = {
        "MessageHeader": [change_of_gp_message_header]
    }

    response = mock_service.handle_message(input_message)

    assert response == expected_response
    mock_map_bundle_entries_to_dict.assert_called_once()
    mock_fhir_bundle.assert_called_once()


@pytest.mark.parametrize(
    "exception_type",
    [
        FhirResourceNotFound({"resourceType": NEMS_ERROR_TYPES.Data, "details": ""}),
        InvalidResourceIdException,
        OdsErrorException,
        OrganisationNotFoundException,
    ],
)
def test_handle_message_returns_data_error_when_handle_change_of_gp_message_raises_FhirResourceNotFound(
    mocker,
    mock_service,
    mock_map_bundle_entries_to_dict,
    mock_fhir_bundle,
    exception_type,
):
    input_message = {
        "body": _valid_change_of_gp_message,
        "messageAttributes": {},
        "messageId": "test-id",
    }
    expected_response = NEMS_ERROR_TYPES.Data
    mock_service.handle_change_of_gp_message = mocker.MagicMock()
    mock_service.handle_change_of_gp_message.side_effect = exception_type
    mock_map_bundle_entries_to_dict.return_value = {
        "MessageHeader": [change_of_gp_message_header]
    }

    response = mock_service.handle_message(input_message)

    assert response == expected_response
    mock_map_bundle_entries_to_dict.assert_called_once()
    mock_fhir_bundle.assert_called_once()


def test_handle_message_when_message_is_valid_but_not_change_of_gp_returns_none(
    mocker, mock_service, mock_fhir_bundle, mock_map_bundle_entries_to_dict
):
    input_message = {
        "body": _valid_non_change_of_gp_message,
        "messageAttributes": {},
        "messageId": "test-id",
    }
    expected_response = None
    mock_map_bundle_entries_to_dict.return_value = {
        "MessageHeader": [non_change_of_gp_bundle.entry[0]]
    }
    mock_service.handle_change_of_gp_message = mocker.MagicMock()

    response = mock_service.handle_message(input_message)

    assert response == expected_response
    mock_map_bundle_entries_to_dict.assert_called_once()
    mock_fhir_bundle.assert_called_once()
    mock_service.handle_change_of_gp_message.assert_not_called()


def test_handle_message_when_message_is_valid_returns_none(
    mocker, mock_service, mock_fhir_bundle, mock_map_bundle_entries_to_dict
):
    input_message = {
        "body": _valid_change_of_gp_message,
        "messageAttributes": {},
        "messageId": "test-id",
    }
    expected_response = None
    mock_service.handle_change_of_gp_message = mocker.MagicMock()
    mock_service.handle_change_of_gp_message.return_value = expected_response
    mock_map_bundle_entries_to_dict.return_value = {
        "MessageHeader": [change_of_gp_message_header]
    }

    response = mock_service.handle_message(input_message)

    assert response == expected_response
    mock_map_bundle_entries_to_dict.assert_called_once()
    mock_fhir_bundle.assert_called_once()
    mock_service.handle_change_of_gp_message.assert_called_once()


######################################################################


def test_handle_change_of_gp_message_when_patient_is_missing_returns_FhirResourceNotFound(
    mock_service,
):
    function_input = {}

    with pytest.raises(FhirResourceNotFound):
        mock_service.handle_change_of_gp_message(function_input)


def test_handle_change_of_gp_message_when_nhs_number_validation_fails_raises_InvalidResourceIdException(
    mock_service, mock_validate_id
):
    function_input = {
        "Patient": [patient_bundle_resource],
        "Organisations": [],
    }
    mock_validate_id.side_effect = InvalidResourceIdException()

    with pytest.raises(InvalidResourceIdException):
        mock_service.handle_change_of_gp_message(function_input)


def test_handle_change_of_gp_message_when_organisations_are_missing_returns_FhirResourceNotFound(
    mock_service,
):
    function_input = {"Patient": [patient_bundle_resource]}

    with pytest.raises(FhirResourceNotFound):
        mock_service.handle_change_of_gp_message(function_input)


def test_handle_change_of_gp_message_when_no_active_gp_resource_throws_FhirResourceNotFound(
    mock_service,
):
    function_input = {
        "Patient": [patient_bundle_resource],
        "Organization": [previous_gp_organisation],
    }

    with pytest.raises(FhirResourceNotFound):
        mock_service.handle_change_of_gp_message(function_input)


def test_handle_change_of_gp_message_nems_validation_throws_OdsErrorException(
    mock_service,
    mock_validate_id,
    mock_update_LG_table_with_current_GP,
    mock_validate_nems_details,
):
    function_input = {
        "Patient": [patient_bundle_resource],
        "Organization": [previous_gp_organisation, active_gp_organisation],
    }
    mock_validate_nems_details.side_effect = OdsErrorException()

    with pytest.raises(OdsErrorException):
        mock_service.handle_change_of_gp_message(function_input)

    mock_update_LG_table_with_current_GP.assert_not_called()
    mock_validate_nems_details.assert_called_once()
    mock_validate_id.assert_called_once()


def test_handle_change_of_gp_message_when_nems_validation_throws_OrganisationNotFoundException(
    mock_service,
    mock_validate_id,
    mock_update_LG_table_with_current_GP,
    mock_validate_nems_details,
):
    function_input = {
        "Patient": [patient_bundle_resource],
        "Organization": [previous_gp_organisation, active_gp_organisation],
    }
    mock_validate_nems_details.side_effect = OrganisationNotFoundException()

    with pytest.raises(OrganisationNotFoundException):
        mock_service.handle_change_of_gp_message(function_input)

    mock_update_LG_table_with_current_GP.assert_not_called()
    mock_validate_nems_details.assert_called_once()
    mock_validate_id.assert_called_once()


def test_handle_change_of_gp_message_happy_path(
    mock_service,
    mock_validate_id,
    mock_update_LG_table_with_current_GP,
    mock_validate_nems_details,
):
    function_input = {
        "Patient": [patient_bundle_resource],
        "Organization": [previous_gp_organisation, active_gp_organisation],
    }

    response = mock_service.handle_change_of_gp_message(function_input)

    assert response is None
    mock_update_LG_table_with_current_GP.assert_called_once()
    mock_validate_nems_details.assert_called_once()
    mock_validate_id.assert_called_once()


def test_validate_nems_details_throws_OdsErrorException(mock_service):
    mock_service.ods_api_service.fetch_organisation_data.side_effect = (
        OdsErrorException()
    )

    with pytest.raises(OdsErrorException):
        mock_service.validate_nems_details("test")


def test_validate_nems_details_throws_OrganisationNotFoundException(mock_service):
    mock_service.ods_api_service.fetch_organisation_data.side_effect = (
        OrganisationNotFoundException()
    )

    with pytest.raises(OrganisationNotFoundException):
        mock_service.validate_nems_details("test")


def test_update_lg_table_when_fetch_raise_client_error(mock_service):
    mock_service.document_service.fetch_documents_from_table.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "mocked error"}}, "test"
    )

    with pytest.raises(ClientError):
        mock_service.update_LG_table_with_current_GP("test_number", "test_ods")

    mock_service.document_service.fetch_documents_from_table.assert_called_once()
    mock_service.document_service.update_documents.assert_not_called()


def test_update_lg_table_when_update_raise_client_error(mock_service):
    mock_service.document_service.fetch_documents_from_table.return_value = {
        "Doc": "test_doc"
    }
    mock_service.document_service.update_documents.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "mocked error"}}, "test"
    )

    with pytest.raises(ClientError):
        mock_service.update_LG_table_with_current_GP("test_number", "test_ods")

    mock_service.document_service.fetch_documents_from_table.assert_called_once()
    mock_service.document_service.update_documents.assert_called_once()


def test_update_lg_table_happy_path(mock_service):
    mock_service.document_service.fetch_documents_from_table.return_value = {
        "Doc": "test_doc"
    }

    mock_service.update_LG_table_with_current_GP("test_number", "test_ods")

    mock_service.document_service.fetch_documents_from_table.assert_called_once()
    mock_service.document_service.update_documents.assert_called_once()


def test_update_lg_table_no_documents(mock_service):
    mock_service.document_service.fetch_documents_from_table.return_value = []

    mock_service.update_LG_table_with_current_GP("test_number", "test_ods")

    mock_service.document_service.fetch_documents_from_table.assert_called_once()
    mock_service.document_service.update_documents.assert_not_called()
