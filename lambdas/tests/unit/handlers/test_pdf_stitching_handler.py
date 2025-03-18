from json import JSONDecodeError

import pytest
from enums.lambda_error import LambdaError
from handlers.pdf_stitching_handler import lambda_handler
from models.sqs.pdf_stitching_sqs_message import PdfStitchingSqsMessage
from pydantic import ValidationError
from services.pdf_stitching_service import PdfStitchingService
from tests.unit.conftest import MOCK_INTERACTION_ID, TEST_NHS_NUMBER
from tests.unit.helpers.data.sqs.test_messages import (
    no_body_message_event,
    stitching_queue_message_event,
)
from utils.lambda_exceptions import PdfStitchingException
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context


@pytest.fixture
def mock_process_message(set_env, mocker):
    yield mocker.patch.object(PdfStitchingService, "process_message")


def test_handler_processes_valid_stitching_message(mock_process_message, context):
    message = {
        "nhs_number": f"{TEST_NHS_NUMBER}",
        "snomed_code_doc_type": {
            "code": "16521000000101",
            "display_name": "Lloyd George record folder",
        },
    }
    test_message = PdfStitchingSqsMessage.model_validate(message)

    expected = ApiGatewayResponse(
        status_code=200,
        body="Successfully processed PDF stitching SQS message",
        methods="GET",
    ).create_api_gateway_response()

    actual = lambda_handler(stitching_queue_message_event, context)

    assert actual == expected
    mock_process_message.assert_called_once_with(stitching_message=test_message)


@pytest.mark.parametrize("invalid_event", [{}, {"Records": []}])
def test_handler_handles_empty_message(context, mock_process_message, invalid_event):
    request_context.request_id = MOCK_INTERACTION_ID
    expected = ApiGatewayResponse(
        status_code=400,
        body=LambdaError.SqsInvalidEvent.create_error_body(),
        methods="GET",
    ).create_api_gateway_response()

    actual = lambda_handler(invalid_event, context)

    assert actual == expected
    mock_process_message.assert_not_called()


@pytest.mark.parametrize(
    ["invalid_event", "exception"],
    [
        (no_body_message_event, JSONDecodeError),
        (
            {"Records": [{"body": f'{{"nhs_number": "{TEST_NHS_NUMBER}"}}'}]},
            ValidationError,
        ),
    ],
)
def test_handler_handles_invalid_message_raises_exception(
    context, mock_process_message, invalid_event, exception
):
    request_context.request_id = MOCK_INTERACTION_ID

    with pytest.raises(exception):
        lambda_handler(invalid_event, context)

    mock_process_message.assert_not_called()


@pytest.mark.parametrize(
    "service_exception",
    [
        PdfStitchingException(400, LambdaError.StitchError),
        PdfStitchingException(400, LambdaError.MultipartError),
    ],
)
def test_handler_handles_service_error_raises_exception(
    context, mock_process_message, service_exception
):
    request_context.request_id = MOCK_INTERACTION_ID
    mock_process_message.side_effect = service_exception

    with pytest.raises(PdfStitchingException):
        lambda_handler(stitching_queue_message_event, context)


def test_handler_handles_rollback_exception(context, mock_process_message):
    request_context.request_id = MOCK_INTERACTION_ID
    mock_process_message.side_effect = PdfStitchingException(
        500, LambdaError.StitchRollbackError
    )

    expected = ApiGatewayResponse(
        status_code=500,
        body="Failed to process PDF stitching SQS message",
        methods="GET",
    ).create_api_gateway_response()

    actual = lambda_handler(stitching_queue_message_event, context)

    assert actual == expected
