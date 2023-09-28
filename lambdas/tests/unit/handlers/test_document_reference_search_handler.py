import json

from botocore.exceptions import ClientError
from handlers.document_reference_search_handler import lambda_handler
from tests.unit.helpers.data.dynamo_responses import (EXPECTED_RESPONSE,
                                                      MOCK_EMPTY_RESPONSE,
                                                      MOCK_RESPONSE)
from utils.exceptions import DynamoDbException, InvalidResourceIdException
from utils.lambda_response import ApiGatewayResponse


def test_lambda_handler_returns_items_from_dynamo_returns_200(
    set_env, valid_id_event, context, mocker
):
    mock_dynamo = mocker.patch("services.dynamo_service.DynamoDBService.query_service")
    mock_dynamo.return_value = MOCK_RESPONSE

    expected = ApiGatewayResponse(
        200, json.dumps(EXPECTED_RESPONSE * 2), "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_event, context)

    assert expected == actual


def test_lambda_handler_returns_items_from_doc_store_only_returns_200(
    set_env, valid_id_event, context, mocker
):
    mock_dynamo = mocker.patch("services.dynamo_service.DynamoDBService.query_service")
    mock_dynamo.side_effect = [MOCK_RESPONSE, MOCK_EMPTY_RESPONSE]

    expected = ApiGatewayResponse(
        200, json.dumps(EXPECTED_RESPONSE), "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_event, context)

    assert expected == actual


def test_lambda_handler_when_dynamo_returns_no_records_returns_204(
    set_env, valid_id_event, context, mocker
):
    mock_dynamo = mocker.patch("services.dynamo_service.DynamoDBService.query_service")
    mock_dynamo.return_value = MOCK_EMPTY_RESPONSE

    expected = ApiGatewayResponse(204, "[]", "GET").create_api_gateway_response()

    actual = lambda_handler(valid_id_event, context)

    assert expected == actual


def test_lambda_handler_raises_DynamoDbException_returns_500(
    set_env, valid_id_event, context, mocker
):
    mock_dynamo = mocker.patch("services.dynamo_service.DynamoDBService.query_service")
    mock_dynamo.side_effect = DynamoDbException

    expected = ApiGatewayResponse(
        500,
        "An error occurred when searching for available documents",
        "GET",
    ).create_api_gateway_response()
    actual = lambda_handler(valid_id_event, context)
    assert expected == actual


def test_lambda_handler_raises_ClientError_returns_500(
    set_env, valid_id_event, context, mocker
):
    mock_dynamo = mocker.patch("services.dynamo_service.DynamoDBService.query_service")
    mock_dynamo.return_value = MOCK_EMPTY_RESPONSE
    mock_dynamo.side_effect = ClientError(
        {"Error": {"Code": 500, "Message": "test error"}}, "testing"
    )

    expected = ApiGatewayResponse(
        500,
        "An error occurred when searching for available documents",
        "GET",
    ).create_api_gateway_response()
    actual = lambda_handler(valid_id_event, context)
    assert expected == actual


def test_lambda_handler_raises_InvalidResourceIdException_returns_500(
    set_env, valid_id_event, context, mocker
):
    exception = InvalidResourceIdException

    mock_dynamo = mocker.patch("services.dynamo_service.DynamoDBService.query_service")
    mock_dynamo.side_effect = exception

    expected = ApiGatewayResponse(
        500, "No data was requested to be returned in query", "GET"
    ).create_api_gateway_response()
    actual = lambda_handler(valid_id_event, context)
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
    valid_id_event, context
):
    expected = ApiGatewayResponse(
        400, "An error occurred due to missing key: 'DYNAMODB_TABLE_LIST'", "GET"
    ).create_api_gateway_response()
    actual = lambda_handler(valid_id_event, context)
    assert expected == actual
