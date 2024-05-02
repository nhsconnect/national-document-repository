import pytest
from enums.supported_document_types import SupportedDocumentTypes
from utils.document_type_utils import extract_document_type_to_enum


@pytest.mark.parametrize(
    "value",
    [
        "LG, ARF",
        "ARF,LG",
        " ARF, LG",
        "LG , ARF",
    ],
)
def test_extract_document_type_both(value):
    expected = SupportedDocumentTypes.ALL

    actual = extract_document_type_to_enum(value)

    assert expected == actual


@pytest.mark.parametrize(
    "value",
    [
        "LG ",
        " LG",
    ],
)
def test_extract_document_type_lg(value):
    expected = SupportedDocumentTypes.LG

    actual = extract_document_type_to_enum(value)

    assert expected == actual


@pytest.mark.parametrize(
    "value",
    [
        "ARF ",
        " ARF",
    ],
)
def test_extract_document_type_arf(value):
    expected = SupportedDocumentTypes.ARF

    actual = extract_document_type_to_enum(value)

    assert expected == actual


@pytest.mark.parametrize(
    ["value", "expected"],
    [
        ("ARF", SupportedDocumentTypes.ARF),
        ("ARF ", SupportedDocumentTypes.ARF),
        (" ARF", SupportedDocumentTypes.ARF),
        ("LG", SupportedDocumentTypes.LG),
        ("LG ", SupportedDocumentTypes.LG),
        (" LG", SupportedDocumentTypes.LG),
        (" ARF, LG ", SupportedDocumentTypes.ALL),
        (" LG  , ARF ", SupportedDocumentTypes.ALL),
    ],
)
def test_extract_document_type_as_enum(value, expected):
    actual = extract_document_type_to_enum(value)

    assert expected == actual
