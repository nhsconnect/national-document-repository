import pytest
from botocore.exceptions import ClientError
from enums.nrl_sqs_upload import NrlActionTypes
from enums.supported_document_types import SupportedDocumentTypes
from enums.virus_scan_result import VirusScanResult
from models.document_reference import DocumentReference
from models.fhir.R4.nrl_fhir_document_reference import Attachment
from models.nrl_sqs_message import NrlSqsMessage
from services.upload_confirm_result_service import UploadConfirmResultService
from tests.unit.conftest import (
    APIM_API_URL,
    MOCK_ARF_BUCKET,
    MOCK_ARF_TABLE_NAME,
    MOCK_LG_BUCKET,
    MOCK_LG_TABLE_NAME,
    MOCK_STAGING_STORE_BUCKET,
    NRL_SQS_URL,
    TEST_FILE_KEY,
    TEST_NHS_NUMBER,
    TEST_UUID,
    MockError,
)
from tests.unit.helpers.data.bulk_upload.test_data import TEST_STAGING_METADATA
from tests.unit.helpers.data.dynamo_responses import MOCK_SEARCH_RESPONSE
from tests.unit.helpers.data.test_documents import create_test_arf_doc_store_refs
from tests.unit.helpers.data.upload_confirm_result import (
    MOCK_ARF_DOCUMENT_REFERENCES,
    MOCK_ARF_DOCUMENTS,
    MOCK_BOTH_DOC_TYPES,
    MOCK_LG_DOCUMENT_REFERENCES,
    MOCK_LG_DOCUMENTS,
    MOCK_LG_SINGLE_DOCUMENT,
    MOCK_NO_DOC_TYPE,
)
from utils.lambda_exceptions import UploadConfirmResultException


@pytest.fixture
def patched_service(set_env, mocker):
    service = UploadConfirmResultService(TEST_NHS_NUMBER)
    mock_dynamo_service = mocker.patch.object(service, "dynamo_service")
    mocker.patch.object(mock_dynamo_service, "update_item")
    mock_s3_service = mocker.patch.object(service, "s3_service")
    mocker.patch.object(mock_s3_service, "copy_across_bucket")
    mocker.patch.object(mock_s3_service, "delete_object")
    mock_document_service = mocker.patch.object(service, "document_service")
    mocker.patch.object(
        mock_document_service, "fetch_available_document_references_by_type"
    )
    mocker.patch.object(service, "sqs_service")
    yield service


@pytest.fixture
def mock_lg_reference(patched_service, mocker):
    mocker.patch.object(
        patched_service.document_service,
        "get_available_lloyd_george_record_for_patient",
    ).return_value = [
        DocumentReference.model_validate(MOCK_SEARCH_RESPONSE["Items"][0])
    ]


@pytest.fixture
def mock_validate_number_of_documents(patched_service, mocker):
    yield mocker.patch.object(patched_service, "validate_number_of_documents")


@pytest.fixture
def mock_verify_virus_scan_result(patched_service, mocker):
    yield mocker.patch.object(patched_service, "verify_virus_scan_result")


@pytest.fixture
def mock_move_files_and_update_dynamo(patched_service, mocker):
    yield mocker.patch.object(patched_service, "move_files_and_update_dynamo")


@pytest.fixture
def mock_update_dynamo_table(patched_service, mocker):
    yield mocker.patch.object(patched_service, "update_dynamo_table")


@pytest.fixture
def mock_copy_files_from_staging_bucket(patched_service, mocker):
    yield mocker.patch.object(patched_service, "copy_files_from_staging_bucket")


@pytest.fixture
def mock_delete_file_from_staging_bucket(patched_service, mocker):
    yield mocker.patch.object(patched_service, "delete_file_from_staging_bucket")


def test_process_documents_with_lg_document_references(
    patched_service,
    mock_validate_number_of_documents,
    mock_move_files_and_update_dynamo,
    mock_verify_virus_scan_result,
):
    patched_service.process_documents(MOCK_LG_DOCUMENTS)

    mock_validate_number_of_documents.assert_called_with(
        SupportedDocumentTypes.LG, MOCK_LG_DOCUMENT_REFERENCES
    )
    mock_move_files_and_update_dynamo.assert_called_with(
        MOCK_LG_DOCUMENT_REFERENCES,
        MOCK_LG_BUCKET,
        MOCK_LG_TABLE_NAME,
        SupportedDocumentTypes.LG.value,
    )


def test_nrl_pointer_created_single_document_uploads(
    patched_service,
    mock_validate_number_of_documents,
    mock_verify_virus_scan_result,
    mock_uuid,
    mock_lg_reference,
):
    mock_nrl_attachment = Attachment(
        url=f"{APIM_API_URL}/DocumentReference/test_file_key",
    )
    mock_nrl_message = NrlSqsMessage(
        nhs_number=TEST_STAGING_METADATA.nhs_number,
        action=NrlActionTypes.CREATE,
        attachment=mock_nrl_attachment,
    )
    patched_service.process_documents(MOCK_LG_SINGLE_DOCUMENT)

    patched_service.sqs_service.send_message_fifo.assert_called_with(
        queue_url=NRL_SQS_URL,
        message_body=mock_nrl_message.model_dump_json(exclude_none=True),
        group_id=f"nrl_sqs_{TEST_UUID}",
    )


def test_message_is_not_sent_to_nrl_sqs_multiple_lg_documents(
    patched_service,
    mock_validate_number_of_documents,
    mock_verify_virus_scan_result,
):
    patched_service.process_documents(MOCK_LG_DOCUMENTS)
    patched_service.sqs_service.send_message_fifo.assert_not_called()


def test_process_documents_with_arf_document_references(
    patched_service,
    mock_validate_number_of_documents,
    mock_move_files_and_update_dynamo,
    mock_verify_virus_scan_result,
):
    patched_service.process_documents(MOCK_ARF_DOCUMENTS)

    mock_validate_number_of_documents.assert_not_called()
    mock_move_files_and_update_dynamo.assert_called_with(
        MOCK_ARF_DOCUMENT_REFERENCES,
        MOCK_ARF_BUCKET,
        MOCK_ARF_TABLE_NAME,
        SupportedDocumentTypes.ARF.value,
    )

    patched_service.sqs_service.send_message_fifo.assert_not_called()


def test_process_documents_with_both_types_of_document_references(
    patched_service,
    mock_validate_number_of_documents,
    mock_move_files_and_update_dynamo,
    mock_verify_virus_scan_result,
    mock_lg_reference,
):
    patched_service.process_documents(MOCK_BOTH_DOC_TYPES)

    mock_validate_number_of_documents.assert_called_once_with(
        SupportedDocumentTypes.LG, [TEST_FILE_KEY]
    )
    assert mock_move_files_and_update_dynamo.call_count == 2


def test_process_documents_when_no_lg_or_arf_doc_type_in_documents_raises_exception(
    patched_service,
    mock_validate_number_of_documents,
    mock_move_files_and_update_dynamo,
):
    with pytest.raises(UploadConfirmResultException):
        patched_service.process_documents(MOCK_NO_DOC_TYPE)

    mock_validate_number_of_documents.assert_not_called()
    mock_move_files_and_update_dynamo.assert_not_called()
    patched_service.sqs_service.send_message_fifo.assert_not_called()


def test_process_documents_when_dynamo_throws_error(
    patched_service, mock_update_dynamo_table
):
    mock_update_dynamo_table.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "test error"}}, "testing"
    )

    with pytest.raises(UploadConfirmResultException):
        patched_service.process_documents(MOCK_ARF_DOCUMENTS)

    patched_service.sqs_service.send_message_fifo.assert_not_called()


def test_process_documents_raise_error_when_some_given_arf_files_are_not_clean(
    patched_service,
    mock_update_dynamo_table,
    mock_move_files_and_update_dynamo,
    mock_verify_virus_scan_result,
):
    mock_verify_virus_scan_result.side_effect = UploadConfirmResultException(
        400, MockError.Error
    )

    with pytest.raises(UploadConfirmResultException):
        patched_service.process_documents(MOCK_ARF_DOCUMENTS)

    mock_verify_virus_scan_result.assert_called_with(
        doc_type=SupportedDocumentTypes.ARF,
        document_references=MOCK_ARF_DOCUMENT_REFERENCES,
    )
    mock_update_dynamo_table.assert_not_called()
    mock_move_files_and_update_dynamo.assert_not_called()
    patched_service.sqs_service.send_message_fifo.assert_not_called()


def test_process_documents_raise_error_when_some_given_lg_files_are_not_clean(
    patched_service,
    mock_update_dynamo_table,
    mock_move_files_and_update_dynamo,
    mock_verify_virus_scan_result,
    mock_validate_number_of_documents,
):
    mock_verify_virus_scan_result.side_effect = UploadConfirmResultException(
        400, MockError.Error
    )

    with pytest.raises(UploadConfirmResultException):
        patched_service.process_documents(MOCK_LG_DOCUMENTS)

    mock_verify_virus_scan_result.assert_called_with(
        doc_type=SupportedDocumentTypes.LG,
        document_references=MOCK_LG_DOCUMENT_REFERENCES,
    )
    mock_update_dynamo_table.assert_not_called()
    mock_move_files_and_update_dynamo.assert_not_called()
    patched_service.sqs_service.send_message_fifo.assert_not_called()


def test_move_files_and_update_dynamo(
    patched_service,
    mock_copy_files_from_staging_bucket,
    mock_delete_file_from_staging_bucket,
    mock_update_dynamo_table,
):
    patched_service.move_files_and_update_dynamo(
        MOCK_ARF_DOCUMENT_REFERENCES,
        MOCK_ARF_BUCKET,
        MOCK_ARF_TABLE_NAME,
        SupportedDocumentTypes.ARF.value,
    )

    mock_copy_files_from_staging_bucket.assert_called_once_with(
        MOCK_ARF_DOCUMENT_REFERENCES, MOCK_ARF_BUCKET, SupportedDocumentTypes.ARF.value
    )
    mock_delete_file_from_staging_bucket.assert_called_with(
        TEST_FILE_KEY, SupportedDocumentTypes.ARF.value
    )
    mock_update_dynamo_table.assert_called_with(
        MOCK_ARF_TABLE_NAME, TEST_FILE_KEY, MOCK_ARF_BUCKET
    )
    assert mock_delete_file_from_staging_bucket.call_count == 2
    assert mock_update_dynamo_table.call_count == 2


def test_copy_files_from_staging_bucket(patched_service):
    patched_service.copy_files_from_staging_bucket(
        MOCK_ARF_DOCUMENT_REFERENCES, MOCK_ARF_BUCKET, SupportedDocumentTypes.ARF.value
    )

    assert patched_service.s3_service.copy_across_bucket.call_count == 2


def test_delete_file_from_staging_bucket(patched_service):
    complete_file_key = f"user_upload/{SupportedDocumentTypes.ARF.value}/{TEST_NHS_NUMBER}/{TEST_FILE_KEY}"

    patched_service.delete_file_from_staging_bucket(
        TEST_FILE_KEY, SupportedDocumentTypes.ARF.value
    )

    patched_service.s3_service.delete_object.assert_called_with(
        MOCK_STAGING_STORE_BUCKET, complete_file_key
    )


def test_update_dynamo_table(patched_service):
    file_location = f"s3://{MOCK_ARF_BUCKET}/{TEST_NHS_NUMBER}/{TEST_FILE_KEY}"

    patched_service.update_dynamo_table(
        MOCK_ARF_TABLE_NAME, TEST_FILE_KEY, MOCK_ARF_BUCKET
    )

    patched_service.dynamo_service.update_item.assert_called_with(
        MOCK_ARF_TABLE_NAME,
        TEST_FILE_KEY,
        {"Uploaded": True, "Uploading": False, "FileLocation": file_location},
    )


def test_validate_number_of_documents_success(patched_service):
    patched_service.document_service.fetch_available_document_references_by_type.return_value = [
        "doc1",
        "doc2",
    ]

    patched_service.validate_number_of_documents(
        MOCK_LG_TABLE_NAME, MOCK_LG_DOCUMENT_REFERENCES
    )

    patched_service.document_service.fetch_available_document_references_by_type.assert_called_once()


def test_validate_number_of_documents_raises_exception(patched_service):
    patched_service.document_service.fetch_available_document_references_by_type.return_value = [
        "doc1",
        "doc2",
        "doc3",
    ]

    with pytest.raises(UploadConfirmResultException):
        patched_service.validate_number_of_documents(
            MOCK_LG_TABLE_NAME, MOCK_LG_DOCUMENT_REFERENCES
        )

    patched_service.document_service.fetch_available_document_references_by_type.assert_called_once()


def test_verify_virus_scan_result_raise_error_if_incoming_file_references_are_unknown(
    patched_service,
):
    test_doc_type = SupportedDocumentTypes.ARF
    mock_clean_records = create_test_arf_doc_store_refs(
        override={"virus_scanner_result": VirusScanResult.CLEAN.value}
    )
    patched_service.document_service.fetch_available_document_references_by_type.return_value = (
        mock_clean_records
    )

    test_document_references = ["doc_id1", "doc_id2"]

    with pytest.raises(UploadConfirmResultException):
        patched_service.verify_virus_scan_result(
            test_doc_type, test_document_references
        )


def test_verify_virus_scan_result_raise_error_if_files_are_not_clean(patched_service):
    test_doc_type = SupportedDocumentTypes.ARF
    mock_unclean_records = create_test_arf_doc_store_refs(
        override={"virus_scanner_result": VirusScanResult.INFECTED.value}
    )
    patched_service.document_service.fetch_available_document_references_by_type.return_value = (
        []
    )

    test_document_references = [record.id for record in mock_unclean_records]

    with pytest.raises(UploadConfirmResultException):
        patched_service.verify_virus_scan_result(
            test_doc_type, test_document_references
        )

    patched_service.sqs_service.send_message_fifo.assert_not_called()


def test_verify_virus_scan_result_should_raise_error_if_newly_uploaded_files_has_some_infected_files(
    patched_service,
):
    test_doc_type = SupportedDocumentTypes.ARF
    mock_clean_records_of_previous_upload = create_test_arf_doc_store_refs(
        override={"virus_scanner_result": VirusScanResult.CLEAN.value}
    )
    mock_new_records_of_upload = create_test_arf_doc_store_refs()
    for index, record in enumerate(mock_new_records_of_upload):
        record.id = f"new_upload_id_{index}"
        if index == 1:
            record.virus_scanner_result = VirusScanResult.INFECTED.value
        else:
            record.virus_scanner_result = VirusScanResult.CLEAN.value

    all_existing_records = (
        mock_clean_records_of_previous_upload + mock_new_records_of_upload
    )
    all_clean_records = [
        record
        for record in all_existing_records
        if record.virus_scanner_result == VirusScanResult.CLEAN.value
    ]
    patched_service.document_service.fetch_available_document_references_by_type.return_value = (
        all_clean_records
    )

    test_document_references = [record.id for record in mock_new_records_of_upload]

    with pytest.raises(UploadConfirmResultException):
        patched_service.verify_virus_scan_result(
            test_doc_type, test_document_references
        )

    patched_service.sqs_service.send_message_fifo.assert_not_called()


def test_verify_virus_scan_result_should_not_raise_error_if_all_files_are_clean(
    patched_service,
):
    test_doc_type = SupportedDocumentTypes.ARF
    mock_clean_records = create_test_arf_doc_store_refs(
        override={"virus_scanner_result": VirusScanResult.CLEAN.value}
    )
    patched_service.document_service.fetch_available_document_references_by_type.return_value = (
        mock_clean_records
    )

    test_document_references = [record.id for record in mock_clean_records]

    patched_service.verify_virus_scan_result(test_doc_type, test_document_references)


def test_verify_virus_scan_result_should_not_raise_error_if_new_uploaded_files_are_all_clean(
    patched_service,
):
    test_doc_type = SupportedDocumentTypes.ARF
    mock_clean_records_of_previous_upload = create_test_arf_doc_store_refs(
        override={"virus_scanner_result": VirusScanResult.CLEAN.value}
    )
    mock_new_records_of_upload = create_test_arf_doc_store_refs(
        override={"virus_scanner_result": VirusScanResult.CLEAN.value}
    )
    for index, record in enumerate(mock_new_records_of_upload):
        record.id = f"new_upload_id_{index}"

    patched_service.document_service.fetch_available_document_references_by_type.return_value = (
        mock_clean_records_of_previous_upload + mock_new_records_of_upload
    )

    test_document_references = [record.id for record in mock_new_records_of_upload]

    patched_service.verify_virus_scan_result(test_doc_type, test_document_references)
