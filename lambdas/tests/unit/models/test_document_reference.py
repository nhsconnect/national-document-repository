import pytest
from models.document_reference import DocumentReference
from utils.exceptions import InvalidDocumentReferenceException

MOCK_DATA = {
    "ID": "3d8683b9-1665-40d2-8499-6e8302d507ff",
    "ContentType": "type",
    "Created": "2023-08-23T00:38:04.095Z",
    "Deleted": "",
    "FileLocation": "s3://test-bucket/9000000009/test-key-123",
    "FileName": "document.csv",
    "NhsNumber": "9000000009",
    "VirusScannerResult": "Clean",
    "CurrentGpOds": "Y12345",
}

MOCK_DOCUMENT_REFERENCE = DocumentReference.model_validate(MOCK_DATA)


def test_get_base_name():
    expected = "document"

    actual = MOCK_DOCUMENT_REFERENCE.get_base_name()

    assert expected == actual


def test_get_file_extension():
    expected = ".csv"

    actual = MOCK_DOCUMENT_REFERENCE.get_file_extension()

    assert expected == actual


def test_get_file_bucket():
    expected = "test-bucket"

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
