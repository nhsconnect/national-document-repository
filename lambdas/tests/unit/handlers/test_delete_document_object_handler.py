import json

import pytest
from handlers.delete_document_object_handler import lambda_handler
from services.document_deletion_service import DocumentDeletionService
from tests.unit.conftest import MockError
from tests.unit.helpers.data.dynamo.dynamo_stream import (
    MOCK_DYNAMO_STREAM_EVENT,
    MOCK_OLD_IMAGE_MODEL,
)
from utils.lambda_exceptions import DocumentDeletionServiceException
from utils.lambda_response import ApiGatewayResponse


@pytest.fixture
def mock_handle_delete(mocker):
    yield mocker.patch.object(DocumentDeletionService, "handle_object_delete")


def test_lambda_handler_valid_dynamo_stream_event_successful_delete_returns_200(
    set_env, context, mock_handle_delete
):
    expected = ApiGatewayResponse(
        200, "Successfully deleted Document Reference object", "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(MOCK_DYNAMO_STREAM_EVENT, context)

    mock_handle_delete.assert_called_once_with(deleted_reference=MOCK_OLD_IMAGE_MODEL)
    assert expected == actual


@pytest.mark.parametrize(
    "invalid_event",
    [
        {},
        {"Records": []},
        {"Records": [{"eventName": "INVALID", "dynamo": {}}]},
        {"Records": [{"eventName": "REMOVE", "dynamo": {"OldImage": {}}}]},
    ],
)
def test_lambda_handler_invalid_dynamo_stream_event_returns_400(
    set_env, invalid_event, context, mock_handle_delete
):
    expected_body = json.dumps(
        {
            "message": "Failed to parse DynamoDb event stream",
            "err_code": "DBS_4001",
            "interaction_id": "88888888-4444-4444-4444-121212121212",
        }
    )
    expected = ApiGatewayResponse(
        400,
        expected_body,
        "GET",
    ).create_api_gateway_response()

    actual = lambda_handler(invalid_event, context)

    assert expected == actual


@pytest.mark.parametrize(
    "invalid_event",
    [
        {
            "Records": [
                {"eventName": "REMOVE", "dynamo": {"OldImage": {"Invalid": "Invalid"}}}
            ]
        },
        {
            "Records": [
                {
                    "eventName": "REMOVE",
                    "dynamo": {
                        "OldImage": {
                            "Deleted": {"S": "2024-12-05T11:58:53.527237Z"},
                        }
                    },
                }
            ]
        },
    ],
)
def test_lambda_handler_invalid_dynamo_stream_image_returns_400(
    set_env, invalid_event, context, mock_handle_delete, caplog
):
    expected_body = json.dumps(
        {
            "message": "Failed to parse DynamoDb event stream",
            "err_code": "DBS_4001",
            "interaction_id": "88888888-4444-4444-4444-121212121212",
        }
    )
    expected = ApiGatewayResponse(
        400,
        expected_body,
        "GET",
    ).create_api_gateway_response()

    actual = lambda_handler(invalid_event, context)

    assert expected == actual


def test_lambda_handler_handles_lambda_exception(set_env, context, mock_handle_delete):
    mock_error = DocumentDeletionServiceException(
        status_code=400, error=MockError.Error
    )
    mock_handle_delete.side_effect = mock_error
    expected_body = json.dumps(MockError.Error.value)
    expected = ApiGatewayResponse(
        400,
        expected_body,
        "GET",
    ).create_api_gateway_response()
    actual = lambda_handler(MOCK_DYNAMO_STREAM_EVENT, context)
    assert expected == actual
