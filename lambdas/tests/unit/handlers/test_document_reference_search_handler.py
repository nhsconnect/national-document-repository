import json
from enum import Enum

import pytest
from handlers.document_reference_search_handler import lambda_handler
from tests.unit.helpers.data.dynamo_responses import EXPECTED_RESPONSE
from utils.lambda_exceptions import DocumentRefSearchException
from utils.lambda_response import ApiGatewayResponse


class MockError(Enum):
    Error = {
        "message": "Client error",
        "err_code": "AB_XXXX",
        "interaction_id": "88888888-4444-4444-4444-121212121212",
    }


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
        500, MockError.Error
    )
    expected = ApiGatewayResponse(
        500,
        json.dumps(MockError.Error.value),
        "GET",
    ).create_api_gateway_response()
    actual = lambda_handler(valid_id_event_without_auth_header, context)
    assert expected == actual


def test_lambda_handler_when_id_not_valid_returns_400(
    set_env, invalid_id_event, context
):
    expected_body = json.dumps(
        {
            "message": "Invalid patient number 900000000900",
            "err_code": "PN_4001",
            "interaction_id": "88888888-4444-4444-4444-121212121212",
        }
    )
    expected = ApiGatewayResponse(
        400, expected_body, "GET"
    ).create_api_gateway_response()
    actual = lambda_handler(invalid_id_event, context)
    assert expected == actual


def test_lambda_handler_when_id_not_supplied_returns_400(
    set_env, missing_id_event, context
):
    expected_body = json.dumps(
        {
            "message": "An error occurred due to missing key",
            "err_code": "PN_4002",
            "interaction_id": "88888888-4444-4444-4444-121212121212",
        }
    )
    expected = ApiGatewayResponse(
        400, expected_body, "GET"
    ).create_api_gateway_response()
    actual = lambda_handler(missing_id_event, context)
    assert expected == actual


def test_lambda_handler_when_dynamo_tables_env_variable_not_supplied_then_return_400_response(
    valid_id_event_without_auth_header, context
):
    expected_body = json.dumps(
        {
            "message": "An error occurred due to missing environment variable: 'DYNAMODB_TABLE_LIST'",
            "err_code": "ENV_5001",
            "interaction_id": "88888888-4444-4444-4444-121212121212",
        }
    )
    expected = ApiGatewayResponse(
        500,
        expected_body,
        "GET",
    ).create_api_gateway_response()
    actual = lambda_handler(valid_id_event_without_auth_header, context)
    assert expected == actual
