import json

import pytest
from enums.supported_document_types import SupportedDocumentTypes
from utils.lambda_response import ApiGatewayResponse

from lambdas.utils.decorators.validate_document_type import (
    extract_document_type,
    extract_document_type_as_enum,
    validate_document_type,
)


@validate_document_type
def lambda_handler(event, context):
    return "200 OK"


def test_runs_lambda_when_receiving_arf_doc_type(
    valid_id_and_arf_doctype_event, context
):
    expected = "200 OK"

    actual = lambda_handler(valid_id_and_arf_doctype_event, context)

    assert actual == expected


def test_runs_lambda_when_receiving_lg_doc_type(valid_id_and_lg_doctype_event, context):
    expected = "200 OK"

    actual = lambda_handler(valid_id_and_lg_doctype_event, context)

    assert actual == expected


def test_runs_lambda_when_receiving_both_doc_types(
    valid_id_and_both_doctype_event, context
):
    expected = "200 OK"

    actual = lambda_handler(valid_id_and_both_doctype_event, context)

    assert actual == expected


def test_returns_400_response_when_doctype_not_supplied(valid_id_event, context):
    body = json.dumps(
        {"message": "An error occurred due to missing key", "err_code": "VDT_4003"}
    )
    expected = ApiGatewayResponse(400, body, "GET").create_api_gateway_response()

    actual = lambda_handler(valid_id_event, context)

    assert actual == expected


def test_returns_400_response_when_invalid_doctype_supplied(
    valid_id_and_invalid_doctype_event, context
):
    body = json.dumps(
        {"message": "Invalid document type requested", "err_code": "VDT_4002"}
    )
    expected = ApiGatewayResponse(400, body, "GET").create_api_gateway_response()

    actual = lambda_handler(valid_id_and_invalid_doctype_event, context)

    assert actual == expected


def test_returns_400_response_when_nonsense_doctype_supplied(
    valid_id_and_nonsense_doctype_event, context
):
    body = json.dumps(
        {"message": "Invalid document type requested", "err_code": "VDT_4002"}
    )
    expected = ApiGatewayResponse(400, body, "GET").create_api_gateway_response()

    actual = lambda_handler(valid_id_and_nonsense_doctype_event, context)

    assert actual == expected


def test_returns_400_response_when_empty_doctype_supplied(
    valid_id_and_empty_doctype_event, context
):
    body = json.dumps(
        {"message": "Invalid document type requested", "err_code": "VDT_4002"}
    )
    expected = ApiGatewayResponse(400, body, "GET").create_api_gateway_response()

    actual = lambda_handler(valid_id_and_empty_doctype_event, context)

    assert actual == expected


def test_returns_400_response_when_doctype_field_not_in_event(
    valid_id_and_none_doctype_event, context
):
    body = json.dumps({"message": "docType not supplied", "err_code": "VDT_4001"})
    expected = ApiGatewayResponse(400, body, "GET").create_api_gateway_response()

    actual = lambda_handler(valid_id_and_none_doctype_event, context)

    assert actual == expected


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
    expected = SupportedDocumentTypes.ALL.value

    actual = extract_document_type(value)

    assert expected == actual


@pytest.mark.parametrize(
    "value",
    [
        "LG ",
        " LG",
    ],
)
def test_extract_document_type_lg(value):
    expected = SupportedDocumentTypes.LG.value

    actual = extract_document_type(value)

    assert expected == actual


@pytest.mark.parametrize(
    "value",
    [
        "ARF ",
        " ARF",
    ],
)
def test_extract_document_type_arf(value):
    expected = SupportedDocumentTypes.ARF.value

    actual = extract_document_type(value)

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
    actual = extract_document_type_as_enum(value)

    assert expected == actual
