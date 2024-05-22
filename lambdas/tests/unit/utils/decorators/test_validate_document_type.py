import json

from utils.lambda_response import ApiGatewayResponse

from lambdas.utils.decorators.validate_document_type import validate_document_type


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
        {
            "message": "An error occurred due to missing key",
            "err_code": "VDT_4003",
            "interaction_id": "88888888-4444-4444-4444-121212121212",
        }
    )
    expected = ApiGatewayResponse(400, body, "GET").create_api_gateway_response()

    actual = lambda_handler(valid_id_event, context)

    assert actual == expected


def test_returns_400_response_when_invalid_doctype_supplied(
    valid_id_and_invalid_doctype_event, context
):
    body = json.dumps(
        {
            "message": "Invalid document type requested",
            "err_code": "VDT_4002",
            "interaction_id": "88888888-4444-4444-4444-121212121212",
        }
    )
    expected = ApiGatewayResponse(400, body, "GET").create_api_gateway_response()

    actual = lambda_handler(valid_id_and_invalid_doctype_event, context)

    assert actual == expected


def test_returns_400_response_when_nonsense_doctype_supplied(
    valid_id_and_nonsense_doctype_event, context
):
    body = json.dumps(
        {
            "message": "Invalid document type requested",
            "err_code": "VDT_4002",
            "interaction_id": "88888888-4444-4444-4444-121212121212",
        }
    )
    expected = ApiGatewayResponse(400, body, "GET").create_api_gateway_response()

    actual = lambda_handler(valid_id_and_nonsense_doctype_event, context)

    assert actual == expected


def test_returns_400_response_when_empty_doctype_supplied(
    valid_id_and_empty_doctype_event, context
):
    body = json.dumps(
        {
            "message": "Invalid document type requested",
            "err_code": "VDT_4002",
            "interaction_id": "88888888-4444-4444-4444-121212121212",
        }
    )
    expected = ApiGatewayResponse(400, body, "GET").create_api_gateway_response()

    actual = lambda_handler(valid_id_and_empty_doctype_event, context)

    assert actual == expected


def test_returns_400_response_when_doctype_field_not_in_event(
    valid_id_and_none_doctype_event, context
):
    body = json.dumps(
        {
            "message": "docType not supplied",
            "err_code": "VDT_4001",
            "interaction_id": "88888888-4444-4444-4444-121212121212",
        }
    )
    expected = ApiGatewayResponse(400, body, "GET").create_api_gateway_response()

    actual = lambda_handler(valid_id_and_none_doctype_event, context)

    assert actual == expected
