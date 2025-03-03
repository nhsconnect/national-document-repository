from random import shuffle

import pytest
from freezegun.api import freeze_time
from tests.unit.conftest import MOCK_LG_BUCKET, TEST_NHS_NUMBER, TEST_UUID
from tests.unit.helpers.data.test_documents import (
    create_test_lloyd_george_doc_store_refs,
)
from utils.lambda_exceptions import PdfStitchingException

from lambdas.services.pdf_stitching_service import PdfStitchingService

TEST_DOCUMENT_REFERENCES = create_test_lloyd_george_doc_store_refs()


@pytest.fixture
def mock_service(set_env, mocker):
    service = PdfStitchingService()
    mocker.patch.object(service, "dynamo_service")
    mocker.patch.object(service, "s3_service")
    mocker.patch.object(service, "document_service")
    mocker.patch.object(service, "sqs_service")
    return service


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


def test_migrate_multipart_references(mock_service):
    mock_service.migrate_multipart_references(TEST_DOCUMENT_REFERENCES)


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
