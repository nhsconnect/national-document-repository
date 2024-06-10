import pytest
from enums.supported_document_types import SupportedDocumentTypes
from tests.unit.conftest import (
    MOCK_ARF_BUCKET,
    MOCK_ARF_TABLE_NAME,
    MOCK_LG_BUCKET,
    MOCK_LG_TABLE_NAME,
)


@pytest.mark.parametrize(
    ["doc_type", "expected"],
    [
        (SupportedDocumentTypes.ARF, MOCK_ARF_TABLE_NAME),
        (SupportedDocumentTypes.LG, MOCK_LG_TABLE_NAME),
    ],
)
def test_get_dynamodb_table_name_return_table_name(set_env, doc_type, expected):
    doc_type_enum = SupportedDocumentTypes(doc_type)
    actual = doc_type_enum.get_dynamodb_table_name()

    assert actual == expected


@pytest.mark.parametrize(
    ["doc_type", "expected"],
    [
        (SupportedDocumentTypes.ARF, MOCK_ARF_BUCKET),
        (SupportedDocumentTypes.LG, MOCK_LG_BUCKET),
    ],
)
def test_get_s3_bucket_name_return_bucket_name(set_env, doc_type, expected):
    doc_type_enum = SupportedDocumentTypes(doc_type)
    actual = doc_type_enum.get_s3_bucket_name()

    assert actual == expected
