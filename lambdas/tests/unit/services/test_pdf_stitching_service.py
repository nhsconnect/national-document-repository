import copy
import json
import os
import sys
from io import BytesIO
from random import shuffle
from unittest.mock import call

import pytest
from enums.lambda_error import LambdaError
from enums.nrl_sqs_upload import NrlActionTypes
from enums.snomed_codes import SnomedCodes
from enums.supported_document_types import SupportedDocumentTypes
from freezegun.api import freeze_time
from models.fhir.R4.fhir_document_reference import Attachment
from models.sqs.nrl_sqs_message import NrlSqsMessage
from models.sqs.pdf_stitching_sqs_message import PdfStitchingSqsMessage
from pypdf import PdfReader, PdfWriter
from tests.unit.conftest import (
    MOCK_CLIENT_ERROR,
    MOCK_LG_BUCKET,
    MOCK_LG_TABLE_NAME,
    MOCK_UNSTITCHED_LG_TABLE_NAME,
    TEST_BASE_DIRECTORY,
    TEST_NHS_NUMBER,
    TEST_UUID,
)
from tests.unit.helpers.data.sqs.test_messages import stitching_queue_message_event
from tests.unit.helpers.data.test_documents import (
    create_singular_test_lloyd_george_doc_store_ref,
    create_test_lloyd_george_doc_store_refs,
)
from utils.lambda_exceptions import PdfStitchingException

from lambdas.services.pdf_stitching_service import PdfStitchingService

TEST_DOCUMENT_REFERENCES = create_test_lloyd_george_doc_store_refs()
TEST_1_OF_1_DOCUMENT_REFERENCE = create_singular_test_lloyd_george_doc_store_ref()


@freeze_time("2025-01-01 12:00:00")
@pytest.fixture
def mock_service(set_env, mocker):
    service = PdfStitchingService()
    mocker.patch.object(service, "dynamo_service")
    mocker.patch.object(service, "s3_service")
    mocker.patch.object(service, "document_service")
    mocker.patch.object(service, "sqs_service")
    service.target_dynamo_table = SupportedDocumentTypes.LG.get_dynamodb_table_name()
    service.target_bucket = SupportedDocumentTypes.LG.get_s3_bucket_name()
    return service


@pytest.fixture
def mock_create_stitched_reference(mocker, mock_service):
    return mocker.patch.object(mock_service, "create_stitched_reference")


@pytest.fixture
def mock_sort_multipart_object_keys(mocker, mock_service):
    return mocker.patch.object(mock_service, "sort_multipart_object_keys")


@pytest.fixture
def mock_process_stitching(mocker, mock_service):
    return mocker.patch.object(mock_service, "process_stitching")


@pytest.fixture
def mock_upload_stitched_file(mocker, mock_service):
    return mocker.patch.object(mock_service, "upload_stitched_file")


@pytest.fixture
def mock_migrate_multipart_references(mocker, mock_service):
    return mocker.patch.object(mock_service, "migrate_multipart_references")


@pytest.fixture
def mock_write_stitching_reference(mocker, mock_service):
    return mocker.patch.object(mock_service, "write_stitching_reference")


@pytest.fixture
def mock_publish_nrl_message(mocker, mock_service):
    return mocker.patch.object(mock_service, "publish_nrl_message")


@pytest.fixture
def mock_retrieve_multipart_references(mocker, mock_service):
    return mocker.patch.object(mock_service, "retrieve_multipart_references")


@pytest.fixture
def mock_rollback_stitching_process(mocker, mock_service):
    return mocker.patch.object(mock_service, "rollback_stitching_process")


@pytest.fixture
def mock_rollback_stitched_reference(mocker, mock_service):
    return mocker.patch.object(mock_service, "rollback_stitched_reference")


@pytest.fixture
def mock_rollback_reference_migration(mocker, mock_service):
    return mocker.patch.object(mock_service, "rollback_reference_migration")


@pytest.fixture
def mock_download_fileobj():
    def _mock_download_fileobj(
        s3_object_data: dict[str, BytesIO], Bucket: str, Key: str, Fileobj: BytesIO
    ):
        if Key in s3_object_data:
            Fileobj.write(s3_object_data[Key].read())
        Fileobj.seek(0)

    return _mock_download_fileobj


@pytest.mark.parametrize(
    "doc_type",
    [
        SupportedDocumentTypes.LG,
        SupportedDocumentTypes.ARF,
    ],
)
def test_retrieve_multipart_references_returns_multipart_references(
    mock_service, doc_type
):
    mock_service.document_service.fetch_available_document_references_by_type.return_value = (
        TEST_DOCUMENT_REFERENCES
    )

    expected = TEST_DOCUMENT_REFERENCES

    actual = mock_service.retrieve_multipart_references(
        nhs_number=TEST_NHS_NUMBER, doc_type=doc_type
    )

    assert expected == actual
    mock_service.document_service.fetch_available_document_references_by_type.assert_called_once()


def test_retrieve_multipart_references_returns_empty_list_if_LG_stitched(mock_service):
    mock_service.document_service.fetch_available_document_references_by_type.return_value = [
        TEST_1_OF_1_DOCUMENT_REFERENCE
    ]

    expected = []

    actual = mock_service.retrieve_multipart_references(
        nhs_number=TEST_NHS_NUMBER, doc_type=SupportedDocumentTypes.LG
    )

    assert expected == actual
    mock_service.document_service.fetch_available_document_references_by_type.assert_called_once()


def test_process_message(
    mock_service,
    mock_retrieve_multipart_references,
    mock_create_stitched_reference,
    mock_sort_multipart_object_keys,
    mock_process_stitching,
    mock_upload_stitched_file,
    mock_migrate_multipart_references,
    mock_write_stitching_reference,
    mock_publish_nrl_message,
):
    test_message_body = json.loads(stitching_queue_message_event["Records"][0]["body"])
    test_message = PdfStitchingSqsMessage.model_validate(test_message_body)
    test_stream = BytesIO()
    test_sorted_keys = [reference.s3_file_key for reference in TEST_DOCUMENT_REFERENCES]

    mock_sort_multipart_object_keys.return_value = test_sorted_keys
    mock_process_stitching.return_value = test_stream
    mock_retrieve_multipart_references.return_value = TEST_DOCUMENT_REFERENCES

    def set_stitched_reference(document_reference, stitch_file_size, *args, **kwargs):
        copied_ref = copy.deepcopy(document_reference)
        copied_ref.s3_file_key = "stitched/key.pdf"
        mock_service.stitched_reference = copied_ref

    mock_create_stitched_reference.side_effect = set_stitched_reference

    mock_service.process_message(test_message)

    mock_create_stitched_reference.assert_called_once_with(
        document_reference=TEST_DOCUMENT_REFERENCES[0],
        stitch_file_size=sys.getsizeof(test_stream),
    )
    mock_sort_multipart_object_keys.assert_called_once_with()
    mock_process_stitching.assert_called_once_with(s3_object_keys=test_sorted_keys)
    mock_upload_stitched_file.assert_called_once_with(stitching_data_stream=test_stream)
    mock_migrate_multipart_references.assert_called_once()
    mock_write_stitching_reference.assert_called_once()
    mock_publish_nrl_message.assert_called_once()


def test_process_message_handles_singular_or_none_references(
    mock_service,
    mock_retrieve_multipart_references,
    mock_create_stitched_reference,
    mock_sort_multipart_object_keys,
    mock_process_stitching,
    mock_upload_stitched_file,
    mock_migrate_multipart_references,
    mock_write_stitching_reference,
    mock_publish_nrl_message,
):
    test_message_body = json.loads(stitching_queue_message_event["Records"][0]["body"])
    test_message = PdfStitchingSqsMessage.model_validate(test_message_body)

    mock_retrieve_multipart_references.return_value = []

    mock_service.process_message(test_message)

    mock_create_stitched_reference.assert_not_called()
    mock_sort_multipart_object_keys.assert_not_called()
    mock_process_stitching.assert_not_called()
    mock_upload_stitched_file.assert_not_called()
    mock_migrate_multipart_references.assert_not_called()
    mock_write_stitching_reference.assert_not_called()
    mock_publish_nrl_message.assert_not_called()


@freeze_time("2025-01-01 12:00:00")
@pytest.mark.parametrize(
    "document_reference",
    [
        TEST_DOCUMENT_REFERENCES[0],
        TEST_DOCUMENT_REFERENCES[1],
        TEST_DOCUMENT_REFERENCES[2],
    ],
)
def test_create_stitched_reference(mock_service, mock_uuid, document_reference):
    assert not mock_service.stitched_reference
    file_size = 1000000000
    mock_service.create_stitched_reference(document_reference, file_size)

    actual = mock_service.stitched_reference

    assert actual.id == TEST_UUID
    assert actual.content_type == "application/pdf"
    assert actual.created == "2025-01-01T12:00:00.000000Z"
    assert actual.deleted is None
    assert (
        actual.file_location == f"s3://{MOCK_LG_BUCKET}/{TEST_NHS_NUMBER}/{TEST_UUID}"
    )
    assert (
        actual.file_name
        == "1of1_Lloyd_George_Record_[Joe Bloggs]_[9000000009]_[30-12-2019].pdf"
    )
    assert actual.nhs_number == TEST_NHS_NUMBER
    assert actual.virus_scanner_result == "Clean"
    assert actual.uploaded is True
    assert actual.uploading is False
    assert actual.last_updated == 1735732800
    assert actual.file_size == file_size
    assert actual.s3_file_key == f"{TEST_NHS_NUMBER}/{TEST_UUID}"
    assert actual.s3_bucket_name == MOCK_LG_BUCKET


def test_process_stitching(mock_service, mock_download_fileobj):
    test_pdf_1 = os.path.join(TEST_BASE_DIRECTORY, "helpers/data/pdf/", "file1.pdf")
    test_pdf_2 = os.path.join(TEST_BASE_DIRECTORY, "helpers/data/pdf/", "file2.pdf")
    test_pdf_3 = os.path.join(TEST_BASE_DIRECTORY, "helpers/data/pdf/", "file3.pdf")

    with open(test_pdf_1, "rb") as file:
        test_pdf_1_bytes = file.read()

    with open(test_pdf_2, "rb") as file:
        test_pdf_2_bytes = file.read()

    with open(test_pdf_3, "rb") as file:
        test_pdf_3_bytes = file.read()

    s3_object_data = {
        "file1.pdf": BytesIO(test_pdf_1_bytes),
        "file2.pdf": BytesIO(test_pdf_2_bytes),
        "file3.pdf": BytesIO(test_pdf_3_bytes),
    }

    expected_writer = PdfWriter()
    expected_writer.add_page(PdfReader(stream=BytesIO(test_pdf_1_bytes)).pages[0])
    expected_writer.add_page(PdfReader(stream=BytesIO(test_pdf_2_bytes)).pages[0])
    expected_writer.add_page(PdfReader(stream=BytesIO(test_pdf_3_bytes)).pages[0])

    expected_stream = BytesIO()
    expected_writer.write(expected_stream)
    expected_stream.seek(0)

    mock_service.s3_service.client.download_fileobj.side_effect = (
        lambda Bucket, Key, Fileobj: mock_download_fileobj(
            s3_object_data, Bucket, Key, Fileobj
        )
    )

    actual_stream = mock_service.process_stitching(list(s3_object_data.keys()))

    assert actual_stream.read() == expected_stream.read()


def test_migrate_multipart_references(mock_service):
    mock_service.multipart_references = TEST_DOCUMENT_REFERENCES
    mock_service.migrate_multipart_references()

    expected_create_calls = [
        call(
            table_name=MOCK_UNSTITCHED_LG_TABLE_NAME,
            item={
                "ContentType": "application/pdf",
                "Created": "2024-01-01T12:00:00.000Z",
                "DocumentScanCreation": "2024-01-01",
                "DocStatus": "final",
                "DocumentSnomedCodeType": "16521000000101",
                "FileLocation": f"{TEST_DOCUMENT_REFERENCES[0].file_location}",
                "FileName": f"{TEST_DOCUMENT_REFERENCES[0].file_name}",
                "ID": f"{TEST_DOCUMENT_REFERENCES[0].id}",
                "LastUpdated": 1704110400,
                "NhsNumber": f"{TEST_DOCUMENT_REFERENCES[0].nhs_number}",
                "Status": "current",
                "Uploaded": True,
                "Uploading": False,
                "Version": "1",
                "VirusScannerResult": "Clean",
            },
        ),
        call(
            table_name=MOCK_UNSTITCHED_LG_TABLE_NAME,
            item={
                "ContentType": "application/pdf",
                "Created": "2024-01-01T12:00:00.000Z",
                "DocStatus": "final",
                "DocumentScanCreation": "2024-01-01",
                "DocumentSnomedCodeType": "16521000000101",
                "FileLocation": f"{TEST_DOCUMENT_REFERENCES[1].file_location}",
                "FileName": f"{TEST_DOCUMENT_REFERENCES[1].file_name}",
                "ID": f"{TEST_DOCUMENT_REFERENCES[1].id}",
                "LastUpdated": 1704110400,
                "NhsNumber": f"{TEST_DOCUMENT_REFERENCES[1].nhs_number}",
                "Status": "current",
                "Version": "1",
                "Uploaded": True,
                "Uploading": False,
                "VirusScannerResult": "Clean",
            },
        ),
        call(
            table_name=MOCK_UNSTITCHED_LG_TABLE_NAME,
            item={
                "ContentType": "application/pdf",
                "Created": "2024-01-01T12:00:00.000Z",
                "DocStatus": "final",
                "DocumentScanCreation": "2024-01-01",
                "DocumentSnomedCodeType": "16521000000101",
                "FileLocation": f"{TEST_DOCUMENT_REFERENCES[2].file_location}",
                "FileName": f"{TEST_DOCUMENT_REFERENCES[2].file_name}",
                "ID": f"{TEST_DOCUMENT_REFERENCES[2].id}",
                "LastUpdated": 1704110400,
                "NhsNumber": f"{TEST_DOCUMENT_REFERENCES[2].nhs_number}",
                "Status": "current",
                "Version": "1",
                "Uploaded": True,
                "Uploading": False,
                "VirusScannerResult": "Clean",
            },
        ),
    ]

    expected_delete_calls = []
    for reference in TEST_DOCUMENT_REFERENCES:
        expected_delete_calls.append(
            call(table_name=MOCK_LG_TABLE_NAME, key={"ID": reference.id})
        )

    assert mock_service.dynamo_service.create_item.call_count == 3
    mock_service.dynamo_service.create_item.assert_has_calls(expected_create_calls)
    assert mock_service.dynamo_service.delete_item.call_count == 3
    mock_service.dynamo_service.delete_item.assert_has_calls(expected_delete_calls)


def test_migrate_multipart_references_handles_client_error_on_create(
    mock_service, caplog
):
    mock_service.multipart_references = TEST_DOCUMENT_REFERENCES
    mock_service.dynamo_service.create_item.side_effect = MOCK_CLIENT_ERROR
    expected_err_msg = (
        "Failed to migrate multipart references: "
        "An error occurred (500) when calling the TEST operation: Test error message"
    )

    with pytest.raises(PdfStitchingException) as e:
        mock_service.migrate_multipart_references()

    assert caplog.records[-1].msg == expected_err_msg
    assert caplog.records[-1].levelname == "ERROR"
    assert e.value.error is LambdaError.MultipartError


def test_migrate_multipart_references_handles_client_error_on_delete(
    mock_service, caplog
):
    mock_service.multipart_references = TEST_DOCUMENT_REFERENCES
    mock_service.dynamo_service.delete_item.side_effect = MOCK_CLIENT_ERROR
    expected_err_msg = (
        "Failed to cleanup multipart references: "
        "An error occurred (500) when calling the TEST operation: Test error message"
    )

    with pytest.raises(PdfStitchingException) as e:
        mock_service.migrate_multipart_references()

    assert caplog.records[-1].msg == expected_err_msg
    assert caplog.records[-1].levelname == "ERROR"
    assert e.value.error is LambdaError.MultipartError


@freeze_time("2024-01-01T12:00:00Z")
def test_write_stitching_reference(mock_service, mock_uuid):
    file_size = 8000
    mock_service.create_stitched_reference(TEST_1_OF_1_DOCUMENT_REFERENCE, file_size)

    mock_service.write_stitching_reference()

    mock_service.dynamo_service.create_item.assert_called_once_with(
        table_name=MOCK_LG_TABLE_NAME,
        item={
            "ContentType": "application/pdf",
            "Created": "2024-01-01T12:00:00.000000Z",
            "DocStatus": "final",
            "DocumentScanCreation": "2024-01-01",
            "DocumentSnomedCodeType": "16521000000101",
            "CurrentGpOds": "Y12345",
            "FileLocation": f"s3://{MOCK_LG_BUCKET}/{TEST_NHS_NUMBER}/{TEST_UUID}",
            "FileName": f"{TEST_1_OF_1_DOCUMENT_REFERENCE.file_name}",
            "ID": f"{TEST_UUID}",
            "LastUpdated": TEST_1_OF_1_DOCUMENT_REFERENCE.last_updated,
            "NhsNumber": f"{TEST_1_OF_1_DOCUMENT_REFERENCE.nhs_number}",
            "FileSize": 8000,
            "Status": "current",
            "Uploaded": True,
            "Uploading": False,
            "Version": "1",
            "VirusScannerResult": "Clean",
        },
    )


def test_write_stitching_reference_handles_client_error(mock_service, caplog):
    mock_service.stitched_reference = TEST_1_OF_1_DOCUMENT_REFERENCE
    mock_service.dynamo_service.create_item.side_effect = MOCK_CLIENT_ERROR
    expected_err_msg = (
        "Failed to create stitching reference: "
        "An error occurred (500) when calling the TEST operation: Test error message"
    )

    with pytest.raises(PdfStitchingException) as e:
        mock_service.write_stitching_reference()

    assert caplog.records[-1].msg == expected_err_msg
    assert caplog.records[-1].levelname == "ERROR"
    assert e.value.error is LambdaError.StitchError


def test_publish_nrl_message(mock_service, mock_uuid):
    mock_service.stitched_reference = TEST_1_OF_1_DOCUMENT_REFERENCE

    expected_apim_attachment = Attachment(
        url=f"https://apim.api.service.uk/DocumentReference/{SnomedCodes.LLOYD_GEORGE.value.code}~{mock_service.stitched_reference.id}",
        contentType="application/pdf",
    )

    expected_nrl_message = NrlSqsMessage(
        nhs_number=mock_service.stitched_reference.nhs_number,
        action=NrlActionTypes.CREATE,
        attachment=expected_apim_attachment,
    )

    mock_service.publish_nrl_message(
        snomed_code_doc_type=SnomedCodes.LLOYD_GEORGE.value
    )

    mock_service.sqs_service.send_message_fifo.assert_called_once_with(
        queue_url="https://test-queue.com",
        message_body=expected_nrl_message.model_dump_json(),
        group_id=f"nrl_sqs_{TEST_UUID}",
    )


def test_publish_nrl_message_handles_client_error(mock_service):
    mock_service.stitched_reference = TEST_1_OF_1_DOCUMENT_REFERENCE
    mock_service.sqs_service.send_message_fifo.side_effect = MOCK_CLIENT_ERROR

    with pytest.raises(PdfStitchingException):
        mock_service.publish_nrl_message(
            snomed_code_doc_type=SnomedCodes.LLOYD_GEORGE.value
        )


def test_sort_multipart_object_keys_sorts_references_and_returns_keys(mock_service):
    mock_service.multipart_references = TEST_DOCUMENT_REFERENCES

    shuffle(mock_service.multipart_references)

    expected = [
        f"{TEST_NHS_NUMBER}/test-key-1",
        f"{TEST_NHS_NUMBER}/test-key-2",
        f"{TEST_NHS_NUMBER}/test-key-3",
    ]

    actual = mock_service.sort_multipart_object_keys()

    assert actual == expected


def test_sort_multipart_object_keys_raises_exception(mock_service):
    mock_service.multipart_references = TEST_DOCUMENT_REFERENCES
    mock_service.multipart_references[0].file_name = "invalid"

    with pytest.raises(PdfStitchingException):
        mock_service.sort_multipart_object_keys()


def test_rollback_stitching_process_successfully_rolls_back(
    mock_service, mock_rollback_stitched_reference, mock_rollback_reference_migration
):
    mock_service.stitched_reference = TEST_1_OF_1_DOCUMENT_REFERENCE
    mock_service.multipart_references = TEST_DOCUMENT_REFERENCES

    mock_service.rollback_stitching_process()

    mock_rollback_stitched_reference.assert_called_once()
    mock_rollback_reference_migration.assert_called_once()


def test_rollback_stitched_reference(mock_service):
    mock_service.stitched_reference = TEST_1_OF_1_DOCUMENT_REFERENCE

    mock_service.rollback_stitched_reference()

    mock_service.dynamo_service.delete_item.assert_called_once_with(
        table_name=MOCK_LG_TABLE_NAME, key={"ID": TEST_1_OF_1_DOCUMENT_REFERENCE.id}
    )
    mock_service.s3_service.delete_object.assert_called_once_with(
        s3_bucket_name=MOCK_LG_BUCKET, file_key=f"{TEST_NHS_NUMBER}/test-key-123"
    )


def test_rollback_stitched_reference_handles_exception(mock_service):
    mock_service.stitched_reference = TEST_1_OF_1_DOCUMENT_REFERENCE
    mock_service.dynamo_service.delete_item.side_effect = MOCK_CLIENT_ERROR

    with pytest.raises(PdfStitchingException):
        mock_service.rollback_stitched_reference()


def test_rollback_reference_migration(mock_service):
    mock_service.multipart_references = TEST_DOCUMENT_REFERENCES
    mock_service.dynamo_service.get_item.side_effect = (
        {},
        {"Item": {"ID": "123"}},
        {},
        {"Item": {"ID": "234"}},
        {},
        {"Item": {"ID": "567"}},
    )

    mock_service.rollback_reference_migration()

    mock_service.dynamo_service.create_item.assert_has_calls(
        [
            call(
                table_name=MOCK_LG_TABLE_NAME,
                item={
                    "ContentType": "application/pdf",
                    "Created": TEST_DOCUMENT_REFERENCES[0].created,
                    "CurrentGpOds": TEST_DOCUMENT_REFERENCES[0].current_gp_ods,
                    "DocStatus": "final",
                    "DocumentScanCreation": "2024-01-01",
                    "DocumentSnomedCodeType": "16521000000101",
                    "FileLocation": f"{TEST_DOCUMENT_REFERENCES[0].file_location}",
                    "FileName": f"{TEST_DOCUMENT_REFERENCES[0].file_name}",
                    "ID": f"{TEST_DOCUMENT_REFERENCES[0].id}",
                    "LastUpdated": 1704110400,
                    "NhsNumber": f"{TEST_DOCUMENT_REFERENCES[0].nhs_number}",
                    "Status": "current",
                    "Version": "1",
                    "Uploaded": True,
                    "Uploading": False,
                    "VirusScannerResult": "Clean",
                },
            ),
            call(
                table_name=MOCK_LG_TABLE_NAME,
                item={
                    "ContentType": "application/pdf",
                    "Created": TEST_DOCUMENT_REFERENCES[1].created,
                    "CurrentGpOds": TEST_DOCUMENT_REFERENCES[1].current_gp_ods,
                    "DocStatus": "final",
                    "DocumentScanCreation": "2024-01-01",
                    "DocumentSnomedCodeType": "16521000000101",
                    "FileLocation": f"{TEST_DOCUMENT_REFERENCES[1].file_location}",
                    "FileName": f"{TEST_DOCUMENT_REFERENCES[1].file_name}",
                    "ID": f"{TEST_DOCUMENT_REFERENCES[1].id}",
                    "LastUpdated": 1704110400,
                    "NhsNumber": f"{TEST_DOCUMENT_REFERENCES[1].nhs_number}",
                    "Status": "current",
                    "Version": "1",
                    "Uploaded": True,
                    "Uploading": False,
                    "VirusScannerResult": "Clean",
                },
            ),
            call(
                table_name=MOCK_LG_TABLE_NAME,
                item={
                    "ContentType": "application/pdf",
                    "Created": TEST_DOCUMENT_REFERENCES[2].created,
                    "CurrentGpOds": TEST_DOCUMENT_REFERENCES[2].current_gp_ods,
                    "DocStatus": "final",
                    "DocumentScanCreation": "2024-01-01",
                    "DocumentSnomedCodeType": "16521000000101",
                    "FileLocation": f"{TEST_DOCUMENT_REFERENCES[2].file_location}",
                    "FileName": f"{TEST_DOCUMENT_REFERENCES[2].file_name}",
                    "ID": f"{TEST_DOCUMENT_REFERENCES[2].id}",
                    "LastUpdated": 1704110400,
                    "NhsNumber": f"{TEST_DOCUMENT_REFERENCES[2].nhs_number}",
                    "Status": "current",
                    "Version": "1",
                    "Uploaded": True,
                    "Uploading": False,
                    "VirusScannerResult": "Clean",
                },
            ),
        ]
    )

    mock_service.dynamo_service.delete_item.assert_has_calls(
        [
            call(
                table_name=MOCK_UNSTITCHED_LG_TABLE_NAME,
                key={"ID": TEST_DOCUMENT_REFERENCES[0].id},
            ),
            call(
                table_name=MOCK_UNSTITCHED_LG_TABLE_NAME,
                key={"ID": TEST_DOCUMENT_REFERENCES[1].id},
            ),
            call(
                table_name=MOCK_UNSTITCHED_LG_TABLE_NAME,
                key={"ID": TEST_DOCUMENT_REFERENCES[2].id},
            ),
        ]
    )


def test_rollback_reference_migration_handles_exception(mock_service):
    mock_service.multipart_references = TEST_DOCUMENT_REFERENCES
    mock_service.dynamo_service.get_item.side_effect = MOCK_CLIENT_ERROR

    with pytest.raises(PdfStitchingException):
        mock_service.rollback_reference_migration()


def test_process_manual_trigger_calls_process_message_for_each_nhs_number(
    mocker, mock_service
):
    test_ods_code = "A12345"
    test_nhs_numbers = ["1234567890", "9876543210"]

    mock_get_nhs_numbers = mocker.patch.object(
        mock_service.document_service,
        "get_nhs_numbers_based_on_ods_code",
        return_value=test_nhs_numbers,
    )
    mock_send_message = mocker.patch(
        "lambdas.services.pdf_stitching_service.SQSService.send_message_standard"
    )

    mock_service.process_manual_trigger(ods_code=test_ods_code, queue_url="url")

    mock_get_nhs_numbers.assert_called_once_with(ods_code=test_ods_code)
    assert mock_send_message.call_count == len(test_nhs_numbers)
