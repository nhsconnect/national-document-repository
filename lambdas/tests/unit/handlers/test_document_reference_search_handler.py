import json

import pytest
from handlers.document_reference_search_handler import lambda_handler
from tests.unit.helpers.data.dynamo_responses import EXPECTED_RESPONSE
from utils.lambda_exceptions import DocumentRefSearchException
from utils.lambda_response import ApiGatewayResponse


@pytest.fixture
def mocked_service(set_env, mocker):
    mocked_class = mocker.patch(
        "handlers.document_reference_search_handler.DocumentReferenceSearchService"
    )
    mocked_service = mocked_class.return_value
    yield mocked_service


def test_lambda_handler_returns_200(
    mocked_service, valid_id_event_without_auth_header, context
):
    mocked_service.get_document_references.return_value = EXPECTED_RESPONSE * 2

    expected = ApiGatewayResponse(
        200, json.dumps(EXPECTED_RESPONSE * 2), "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_event_without_auth_header, context)

    assert expected == actual


def test_lambda_handler_returns_204(
    mocked_service, valid_id_event_without_auth_header, context
):
    mocked_service.get_document_references.return_value = []

    expected = ApiGatewayResponse(
        204, json.dumps([]), "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_event_without_auth_header, context)

    assert expected == actual


def test_lambda_handler_raises_exception_returns_500(
    mocked_service, valid_id_event_without_auth_header, context
):
    mocked_service.get_document_references.side_effect = DocumentRefSearchException(
        500, "DFS_XXXX", "test_string"
    )
    expected = ApiGatewayResponse(
        500, "test_string", "GET", "DFS_XXXX"
    ).create_api_gateway_response()
    actual = lambda_handler(valid_id_event_without_auth_header, context)
    assert expected == actual


def test_lambda_handler_when_id_not_valid_returns_400(
    set_env, invalid_id_event, context
):
    expected = ApiGatewayResponse(
        400, "Invalid NHS number", "GET"
    ).create_api_gateway_response()
    actual = lambda_handler(invalid_id_event, context)
    assert expected == actual


def test_lambda_handler_when_id_not_supplied_returns_400(
    set_env, missing_id_event, context
):
    expected = ApiGatewayResponse(
        400, "An error occurred due to missing key: 'patientId'", "GET"
    ).create_api_gateway_response()
    actual = lambda_handler(missing_id_event, context)
    assert expected == actual


def test_lambda_handler_when_dynamo_tables_env_variable_not_supplied_then_return_400_response(
    valid_id_event_without_auth_header, context
):
    expected = ApiGatewayResponse(
        500,
        "An error occurred due to missing environment variable: 'DYNAMODB_TABLE_LIST'",
        "GET",
    ).create_api_gateway_response()
    actual = lambda_handler(valid_id_event_without_auth_header, context)
    assert expected == actual
