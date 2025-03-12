import json
import os
from io import BytesIO
from random import shuffle
from unittest.mock import call

import pytest
from enums.lambda_error import LambdaError
from enums.metadata_field_names import DocumentReferenceMetadataFields
from enums.nrl_sqs_upload import NrlActionTypes
from freezegun.api import freeze_time
from models.fhir.R4.nrl_fhir_document_reference import Attachment
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


@pytest.fixture
def mock_service(set_env, mocker):
    service = PdfStitchingService()
    mocker.patch.object(service, "dynamo_service")
    mocker.patch.object(service, "s3_service")
    mocker.patch.object(service, "document_service")
    mocker.patch.object(service, "sqs_service")
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
def mock_download_fileobj():
    def _mock_download_fileobj(
        s3_object_data: dict[str, BytesIO], Bucket: str, Key: str, Fileobj: BytesIO
    ):
        if Key in s3_object_data:
            Fileobj.write(s3_object_data[Key].read())
        Fileobj.seek(0)

    return _mock_download_fileobj


def test_process_message(
    mock_service,
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
    test_sorted_keys = [
        reference.get_file_key() for reference in TEST_DOCUMENT_REFERENCES
    ]

    mock_sort_multipart_object_keys.return_value = test_sorted_keys
    mock_process_stitching.return_value = test_stream

    mock_service.document_service.fetch_available_document_references_by_type.return_value = (
        TEST_DOCUMENT_REFERENCES
    )

    mock_service.process_message(test_message)

    mock_create_stitched_reference.assert_called_once_with(
        document_reference=TEST_DOCUMENT_REFERENCES[0]
    )
    mock_sort_multipart_object_keys.assert_called_once_with(
        document_references=TEST_DOCUMENT_REFERENCES
    )
    mock_process_stitching.assert_called_once_with(s3_object_keys=test_sorted_keys)
    mock_upload_stitched_file.assert_called_once_with(stitching_data_stream=test_stream)
    mock_migrate_multipart_references.assert_called_once_with(
        multipart_references=TEST_DOCUMENT_REFERENCES
    )
    mock_write_stitching_reference.assert_called_once()
    mock_publish_nrl_message.assert_called_once()


@pytest.mark.parametrize(
    "document_references",
    [
        [],
        [TEST_1_OF_1_DOCUMENT_REFERENCE],
    ],
)
def test_process_message_handles_singular_or_none_references(
    mock_service,
    mock_create_stitched_reference,
    mock_sort_multipart_object_keys,
    mock_process_stitching,
    mock_upload_stitched_file,
    mock_migrate_multipart_references,
    mock_write_stitching_reference,
    mock_publish_nrl_message,
    document_references,
):
    test_message_body = json.loads(stitching_queue_message_event["Records"][0]["body"])
    test_message = PdfStitchingSqsMessage.model_validate(test_message_body)

    mock_service.document_service.fetch_available_document_references_by_type.return_value = (
        document_references
    )

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

    mock_service.create_stitched_reference(document_reference)

    actual = mock_service.stitched_reference

    assert actual.id == TEST_UUID
    assert actual.content_type == "application/pdf"
    assert actual.created == "2025-01-01T12:00:00.000000Z"
    assert actual.deleted == ""
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


def test_upload_stitched_file(mock_service):
    mock_service.stitched_reference = TEST_1_OF_1_DOCUMENT_REFERENCE
    test_stream = BytesIO()

    mock_service.upload_stitched_file(test_stream)

    mock_service.s3_service.client.upload_fileobj.assert_called_with(
        Fileobj=test_stream,
        Bucket=MOCK_LG_BUCKET,
        Key=f"{TEST_NHS_NUMBER}/test-key-123",
    )


def test_upload_stitched_file_handles_client_error(mock_service, caplog):
    mock_service.stitched_reference = TEST_1_OF_1_DOCUMENT_REFERENCE
    mock_service.s3_service.client.upload_fileobj.side_effect = MOCK_CLIENT_ERROR
    expected_err_msg = (
        "Failed to upload stitched file to S3: "
        "An error occurred (500) when calling the TEST operation: Test error message"
    )

    with pytest.raises(PdfStitchingException) as e:
        mock_service.upload_stitched_file(BytesIO())

    assert caplog.records[-1].msg == expected_err_msg
    assert caplog.records[-1].levelname == "ERROR"
    assert e.value.error is LambdaError.StitchError


def test_migrate_multipart_references(mock_service):
    mock_service.migrate_multipart_references(TEST_DOCUMENT_REFERENCES)

    expected_create_calls = []
    expected_delete_calls = []
    for reference in TEST_DOCUMENT_REFERENCES:
        expected_item = reference.model_dump_dynamo()
        expected_item.pop(DocumentReferenceMetadataFields.CURRENT_GP_ODS.value)
        expected_create_calls.append(
            call(
                table_name=MOCK_UNSTITCHED_LG_TABLE_NAME,
                item=expected_item,
            )
        )
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
    mock_service.dynamo_service.create_item.side_effect = MOCK_CLIENT_ERROR
    expected_err_msg = (
        "Failed to migrate multipart references: "
        "An error occurred (500) when calling the TEST operation: Test error message"
    )

    with pytest.raises(PdfStitchingException) as e:
        mock_service.migrate_multipart_references(TEST_DOCUMENT_REFERENCES)

    assert caplog.records[-1].msg == expected_err_msg
    assert caplog.records[-1].levelname == "ERROR"
    assert e.value.error is LambdaError.MultipartError


def test_migrate_multipart_references_handles_client_error_on_delete(
    mock_service, caplog
):
    mock_service.dynamo_service.delete_item.side_effect = MOCK_CLIENT_ERROR
    expected_err_msg = (
        "Failed to cleanup multipart references: "
        "An error occurred (500) when calling the TEST operation: Test error message"
    )

    with pytest.raises(PdfStitchingException) as e:
        mock_service.migrate_multipart_references(TEST_DOCUMENT_REFERENCES)

    assert caplog.records[-1].msg == expected_err_msg
    assert caplog.records[-1].levelname == "ERROR"
    assert e.value.error is LambdaError.MultipartError


def test_write_stitching_reference(mock_service):
    mock_service.stitched_reference = TEST_1_OF_1_DOCUMENT_REFERENCE

    mock_service.write_stitching_reference()

    mock_service.dynamo_service.create_item.assert_called_with(
        table_name=MOCK_LG_TABLE_NAME,
        item=TEST_1_OF_1_DOCUMENT_REFERENCE.model_dump_dynamo(),
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
        url=f"https://apim.api.service.uk/DocumentReference/16521000000101~{mock_service.stitched_reference.id}",
        contentType="application/pdf",
    )

    expected_nrl_message = NrlSqsMessage(
        nhs_number=mock_service.stitched_reference.nhs_number,
        action=NrlActionTypes.CREATE,
        attachment=expected_apim_attachment,
    )

    mock_service.publish_nrl_message()

    mock_service.sqs_service.send_message_fifo.assert_called_once_with(
        queue_url="https://test-queue.com",
        message_body=expected_nrl_message.model_dump_json(),
        group_id=f"nrl_sqs_{TEST_UUID}",
    )


def test_publish_nrl_message_handles_client_error(mock_service, caplog):
    mock_service.stitched_reference = TEST_1_OF_1_DOCUMENT_REFERENCE
    mock_service.sqs_service.send_message_fifo.side_effect = MOCK_CLIENT_ERROR

    expected_err_msg = (
        "Failed to publish NRL message onto SQS: "
        "An error occurred (500) when calling the TEST operation: Test error message"
    )

    with pytest.raises(PdfStitchingException) as e:
        mock_service.publish_nrl_message()

    assert caplog.records[-1].msg == expected_err_msg
    assert caplog.records[-1].levelname == "ERROR"
    assert e.value.error is LambdaError.StitchError


def test_publish_nrl_message_handles_error():
    pass


def test_sort_multipart_object_keys_sorts_references_and_returns_keys():
    test_document_references = TEST_DOCUMENT_REFERENCES

    shuffle(test_document_references)

    expected = [
        f"{TEST_NHS_NUMBER}/test-key-1",
        f"{TEST_NHS_NUMBER}/test-key-2",
        f"{TEST_NHS_NUMBER}/test-key-3",
    ]

    actual = PdfStitchingService.sort_multipart_object_keys(test_document_references)

    assert expected == actual


def test_sort_multipart_object_keys_raises_exception():
    test_document_references = TEST_DOCUMENT_REFERENCES
    test_document_references[0].file_name = "invalid"

    with pytest.raises(PdfStitchingException):
        PdfStitchingService.sort_multipart_object_keys(test_document_references)
