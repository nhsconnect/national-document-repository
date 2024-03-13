import pytest
from models.document_reference import DocumentReference
from tests.unit.helpers.data.dynamo_responses import MOCK_SEARCH_RESPONSE
from utils.exceptions import InvalidDocumentReferenceException

MOCK_DOCUMENT_REFERENCE = DocumentReference.model_validate(
    MOCK_SEARCH_RESPONSE["Items"][0]
)


def test_get_base_name():
    expected = "document"

    actual = MOCK_DOCUMENT_REFERENCE.get_base_name()

    assert expected == actual


def test_get_file_extension():
    expected = ".csv"

    actual = MOCK_DOCUMENT_REFERENCE.get_file_extension()

    assert expected == actual


def test_get_file_bucket():
    expected = "test-s3-bucket"

    actual = MOCK_DOCUMENT_REFERENCE.get_file_bucket()

    assert expected == actual


def test_get_file_key():
    expected = "9000000009/test-key-123"

    actual = MOCK_DOCUMENT_REFERENCE.get_file_key()

    assert expected == actual


def test_get_file_bucket_raises_InvalidDocumentReferenceException():
    MOCK_DOCUMENT_REFERENCE.file_location = "s3://"

    with pytest.raises(InvalidDocumentReferenceException):
        MOCK_DOCUMENT_REFERENCE.get_file_bucket()


def test_get_file_key_raises_InvalidDocumentReferenceException():
    MOCK_DOCUMENT_REFERENCE.file_location = "s3://test-bucket"

    with pytest.raises(InvalidDocumentReferenceException):
        MOCK_DOCUMENT_REFERENCE.get_file_key()
