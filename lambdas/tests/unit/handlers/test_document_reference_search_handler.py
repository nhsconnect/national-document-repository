import json
import os
from unittest.mock import patch

from botocore.exceptions import ClientError
from handlers.document_reference_search_handler import lambda_handler
from services.dynamo_query_service import DynamoQueryService
from tests.unit.helpers.data.dynamo_responses import (EXPECTED_RESPONSE,
                                                      MOCK_EMPTY_RESPONSE,
                                                      MOCK_RESPONSE)
from utils.exceptions import DynamoDbException, InvalidResourceIdException
from utils.lambda_response import ApiGatewayResponse

PATCH_ENV_VAR = {
    "DOCUMENT_STORE_DYNAMODB_NAME": "a_real_table",
    "LLOYD_GEORGE_DYNAMODB_NAME": "another_real_table",
}


def test_lambda_handler_returns_items_from_dynamo(valid_id_event, context):
    with patch.dict(os.environ, PATCH_ENV_VAR):
        with patch.object(DynamoQueryService, "__call__", return_value=MOCK_RESPONSE):
            expected = ApiGatewayResponse(
                200, json.dumps(EXPECTED_RESPONSE * 2), "GET"
            ).create_api_gateway_response()
            actual = lambda_handler(valid_id_event, context)

            assert expected
            assert expected == actual


def test_lambda_handler_returns_items_from_doc_store_only(valid_id_event, context):
    with patch.dict(os.environ, PATCH_ENV_VAR):
        with patch.object(
            DynamoQueryService,
            "__call__",
            side_effect=[MOCK_RESPONSE, MOCK_EMPTY_RESPONSE],
        ):
            expected = ApiGatewayResponse(
                200, json.dumps(EXPECTED_RESPONSE), "GET"
            ).create_api_gateway_response()
            actual = lambda_handler(valid_id_event, context)
            assert expected == actual


def test_lambda_handler_returns_204_empty_list_when_dynamo_returns_no_records(
    valid_id_event, context
):
    with patch.dict(os.environ, PATCH_ENV_VAR):
        with patch.object(
            DynamoQueryService, "__call__", return_value=MOCK_EMPTY_RESPONSE
        ):
            expected = ApiGatewayResponse(
                204, "[]", "GET"
            ).create_api_gateway_response()
            actual = lambda_handler(valid_id_event, context)
            assert expected == actual


def test_lambda_handler_returns_500_when_dynamo_has_unexpected_response(
    valid_id_event, context
):
    with patch.dict(os.environ, PATCH_ENV_VAR):
        with patch.object(
            DynamoQueryService,
            "__call__",
            side_effect=DynamoDbException("Unrecognised response from DynamoDB"),
        ):
            expected = ApiGatewayResponse(
                500,
                "An error occurred when searching for available documents: Unrecognised response from DynamoDB",
                "GET",
            ).create_api_gateway_response()
            actual = lambda_handler(valid_id_event, context)
            assert expected == actual


def test_lambda_handler_returns_400_when_id_not_valid(invalid_id_event, context):
    with patch.dict(os.environ, PATCH_ENV_VAR):
        expected = ApiGatewayResponse(
            400, "Invalid NHS number", "GET"
        ).create_api_gateway_response()
        actual = lambda_handler(invalid_id_event, context)
        assert expected == actual


def test_lambda_handler_returns_400_when_id_not_supplied(missing_id_event, context):
    with patch.dict(os.environ, PATCH_ENV_VAR):
        expected = ApiGatewayResponse(
            400, "Please supply an NHS number", "GET"
        ).create_api_gateway_response()
        actual = lambda_handler(missing_id_event, context)
        assert expected == actual


def test_lambda_handler_returns_500_when_client_error_thrown(valid_id_event, context):
    error = {"Error": {"Code": 500, "Message": "DynamoDB is down"}}

    exception = ClientError(error, "Query")
    with patch.dict(os.environ, PATCH_ENV_VAR):
        with patch.object(DynamoQueryService, "__call__", side_effect=exception):
            expected = ApiGatewayResponse(
                500, "An error occurred when searching for available documents", "GET"
            ).create_api_gateway_response()
            actual = lambda_handler(valid_id_event, context)
            assert expected == actual


def test_lambda_handler_returns_400_when_no_fields_requested(valid_id_event, context):
    exception = InvalidResourceIdException
    with patch.dict(os.environ, PATCH_ENV_VAR):
        with patch.object(DynamoQueryService, "__call__", side_effect=exception):
            expected = ApiGatewayResponse(
                500, "No data was requested to be returned in query", "GET"
            ).create_api_gateway_response()
            actual = lambda_handler(valid_id_event, context)
            assert expected == actual
