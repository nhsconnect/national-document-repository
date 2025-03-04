import os
from random import shuffle

import pytest
from enums.lambda_error import LambdaError
from freezegun.api import freeze_time
from models.sqs.pdf_stitching_sqs_message import PdfStitchingSqsMessage
from pypdf import PdfReader, PdfWriter
from six import BytesIO
from tests.unit.conftest import (
    MOCK_CLIENT_ERROR,
    MOCK_LG_BUCKET,
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


def test_process_message(mock_service):
    test_message_body = stitching_queue_message_event["Records"][0]["body"]
    test_message = PdfStitchingSqsMessage.model_validate(test_message_body)

    mock_service.document_service.fetch_available_document_references_by_type.return_value = [
        TEST_DOCUMENT_REFERENCES
    ]
    mock_service.process_message(test_message)


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
    mock_upload_stitched_file,
    mock_migrate_multipart_references,
    mock_write_stitching_reference,
    mock_publish_nrl_message,
    document_references,
):
    test_message_body = stitching_queue_message_event["Records"][0]["body"]
    test_message = PdfStitchingSqsMessage.model_validate(test_message_body)

    mock_service.document_service.fetch_available_document_references_by_type.return_value = (
        document_references
    )

    mock_service.process_message(test_message)

    mock_create_stitched_reference.assert_not_called()
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
    test_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_pdf_1 = os.path.join(test_base_dir, "helpers/data/pdf/", "file1.pdf")
    test_pdf_2 = os.path.join(test_base_dir, "helpers/data/pdf/", "file2.pdf")
    test_pdf_3 = os.path.join(test_base_dir, "helpers/data/pdf/", "file3.pdf")

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

    writer = PdfWriter()
    writer.add_page(PdfReader(BytesIO(test_pdf_1_bytes)).pages[0])
    writer.add_page(PdfReader(BytesIO(test_pdf_2_bytes)).pages[0])
    writer.add_page(PdfReader(BytesIO(test_pdf_3_bytes)).pages[0])

    expected_stream = BytesIO()
    writer.write(expected_stream)
    expected_stream.seek(0)

    mock_service.s3_service.client.download_fileobj.side_effect = (
        lambda Bucket, Key, Fileobj: mock_download_fileobj(
            s3_object_data, Bucket, Key, Fileobj
        )
    )

    actual_stream = mock_service.process_stitching(list(s3_object_data.keys()))

    assert actual_stream.read() == expected_stream.read()


def test_upload_stitched_file():
    pass


def test_upload_stitched_file_handles_client_error(mock_service, caplog):
    mock_service.stitched_reference = TEST_1_OF_1_DOCUMENT_REFERENCE
    mock_service.s3_service.client.upload_fileobj.side_effect = MOCK_CLIENT_ERROR
    expected_err_msg = (
        "Failed to upload stitched file to S3: "
        "An error occurred (500) when calling the Query operation: Test error message"
    )

    with pytest.raises(PdfStitchingException) as e:
        mock_service.upload_stitched_file(BytesIO())

    assert caplog.records[-1].msg == expected_err_msg
    assert caplog.records[-1].levelname == "ERROR"
    assert e.value.error is LambdaError.StitchError


def test_migrate_multipart_references(mock_service):
    mock_service.migrate_multipart_references(TEST_DOCUMENT_REFERENCES)

    assert mock_service.dynamo_service.create_item.call_count == 3
    assert mock_service.dynamo_service.delete_item.call_count == 3


def test_migrate_multipart_references_handles_client_error_on_create(
    mock_service, caplog
):
    mock_service.dynamo_service.create_item.side_effect = MOCK_CLIENT_ERROR
    expected_err_msg = (
        "Failed to migrate multipart references: "
        "An error occurred (500) when calling the Query operation: Test error message"
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
        "An error occurred (500) when calling the Query operation: Test error message"
    )

    with pytest.raises(PdfStitchingException) as e:
        mock_service.migrate_multipart_references(TEST_DOCUMENT_REFERENCES)

    assert caplog.records[-1].msg == expected_err_msg
    assert caplog.records[-1].levelname == "ERROR"
    assert e.value.error is LambdaError.MultipartError


def test_write_stitching_reference():
    pass


def test_write_stitching_reference_handles_client_error():
    pass


def test_publish_nrl_message():
    pass


def test_publish_nrl_message_handles_error():
    pass


def test_process_object_keys_sorts_references_and_returns_keys():
    test_document_references = TEST_DOCUMENT_REFERENCES

    shuffle(test_document_references)

    expected = [
        f"{TEST_NHS_NUMBER}/test-key-1",
        f"{TEST_NHS_NUMBER}/test-key-2",
        f"{TEST_NHS_NUMBER}/test-key-3",
    ]

    actual = PdfStitchingService.process_object_keys(test_document_references)

    assert expected == actual


def test_process_object_keys_handles_and_raises_exception():
    test_document_references = TEST_DOCUMENT_REFERENCES
    test_document_references[0].file_name = "invalid"

    with pytest.raises(PdfStitchingException):
        PdfStitchingService.process_object_keys(test_document_references)
