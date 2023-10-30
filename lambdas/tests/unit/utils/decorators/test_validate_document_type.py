from utils.decorators.validate_document_type import validate_document_type
from utils.lambda_response import ApiGatewayResponse


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
    expected = ApiGatewayResponse(
        400, "An error occurred due to missing key: 'docType'", "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_event, context)

    assert actual == expected


def test_returns_400_response_when_invalid_doctype_supplied(
    valid_id_and_invalid_doctype_event, context
):
    expected = ApiGatewayResponse(
        400, "Invalid document type requested", "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_and_invalid_doctype_event, context)

    assert actual == expected


def test_returns_400_response_when_nonsense_doctype_supplied(
    valid_id_and_nonsense_doctype_event, context
):
    expected = ApiGatewayResponse(
        400, "Invalid document type requested", "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_and_nonsense_doctype_event, context)

    assert actual == expected


def test_returns_400_response_when_empty_doctype_supplied(
    valid_id_and_empty_doctype_event, context
):
    expected = ApiGatewayResponse(
        400, "Invalid document type requested", "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_and_empty_doctype_event, context)

    assert actual == expected


def test_returns_400_response_when_doctype_field_not_in_event(
    valid_id_and_none_doctype_event, context
):
    expected = ApiGatewayResponse(
        400, "docType not supplied", "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_and_none_doctype_event, context)

    assert actual == expected
