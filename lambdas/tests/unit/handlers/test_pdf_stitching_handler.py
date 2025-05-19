from json import JSONDecodeError

import pytest
from enums.lambda_error import LambdaError
from handlers.pdf_stitching_handler import handle_sqs_request, lambda_handler
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
    mock_process = mocker.patch.object(PdfStitchingService, "process_message")
    mock_process_manual_trigger = mocker.patch.object(
        PdfStitchingService, "process_manual_trigger"
    )
    yield mock_process, mock_process_manual_trigger


@pytest.fixture
def mock_pdf_stitching_service(mocker):
    mock_service = mocker.Mock()
    mocker.patch(
        "handlers.pdf_stitching_handler.PdfStitchingService", return_value=mock_service
    )
    return mock_service


def test_lambda_handler_routes_to_sqs(
    mocker, context, mock_process_message, mock_pdf_stitching_service
):
    mock_process, _ = mock_process_message
    event = {
        "ods_code": "Y12345",
        "Records": [{"eventSource": "aws:sqs", "body": "mock body"}],
    }
    mock_handle_sqs_request = mocker.patch(
        "handlers.pdf_stitching_handler.handle_sqs_request"
    )

    lambda_handler(event, context)

    mock_handle_sqs_request.assert_called_once_with(event, mock_pdf_stitching_service)


def test_lambda_handler_manually_triggers(
    mocker, context, mock_process_message, mock_pdf_stitching_service
):
    mock_process, _ = mock_process_message
    event = {
        "ods_code": "Y12345",
        "Records": [{"eventSource": "something", "body": "mock body"}],
    }
    mock_handle_manual_trigger = mocker.patch(
        "handlers.pdf_stitching_handler.handle_manual_trigger"
    )

    lambda_handler(event, context)

    mock_handle_manual_trigger.assert_called_once_with(
        event, mock_pdf_stitching_service
    )


def test_handler_processes_valid_stitching_message(
    mock_process_message, context, mock_pdf_stitching_service
):
    message = {
        "nhs_number": f"{TEST_NHS_NUMBER}",
        "snomed_code_doc_type": {
            "code": "16521000000101",
            "display_name": "Lloyd George record folder",
        },
    }
    test_message = PdfStitchingSqsMessage.model_validate(
        message,
    )

    expected = ApiGatewayResponse(
        status_code=200,
        body="Successfully processed PDF stitching SQS message",
        methods="GET",
    ).create_api_gateway_response()

    actual = lambda_handler(stitching_queue_message_event, context)

    assert actual == expected
    mock_pdf_stitching_service.process_message.assert_called_once_with(
        stitching_message=test_message
    )


@pytest.mark.parametrize("invalid_event", [{}, {"Records": []}])
def test_handler_handles_empty_message(context, mock_process_message, invalid_event):
    mock_process, _ = mock_process_message
    request_context.request_id = MOCK_INTERACTION_ID
    expected = ApiGatewayResponse(
        status_code=400,
        body=LambdaError.SqsInvalidEvent.create_error_body(),
        methods="GET",
    ).create_api_gateway_response()

    actual = handle_sqs_request(invalid_event, context)

    assert actual == expected
    mock_process.assert_not_called()


@pytest.mark.parametrize(
    ["invalid_event", "exception"],
    [
        (no_body_message_event, JSONDecodeError),
        (
            {
                "Records": [
                    {
                        "body": f'{{"nhs_number": "{TEST_NHS_NUMBER}"}}',
                        "eventSource": "aws:sqs",
                    }
                ]
            },
            ValidationError,
        ),
    ],
)
def test_handler_handles_invalid_message_raises_exception(
    context, mock_process_message, invalid_event, exception
):
    mock_process, _ = mock_process_message
    request_context.request_id = MOCK_INTERACTION_ID

    with pytest.raises(exception):
        lambda_handler(invalid_event, context)

    mock_process.assert_not_called()


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
    mock_process, _ = mock_process_message
    request_context.request_id = MOCK_INTERACTION_ID
    mock_process.side_effect = service_exception

    with pytest.raises(PdfStitchingException):
        lambda_handler(stitching_queue_message_event, context)


def test_handler_handles_rollback_exception(context, mock_process_message):
    mock_process, _ = mock_process_message
    request_context.request_id = MOCK_INTERACTION_ID
    mock_process.side_effect = PdfStitchingException(
        500, LambdaError.StitchRollbackError
    )

    expected = ApiGatewayResponse(
        status_code=500,
        body="Failed to process PDF stitching SQS message",
        methods="GET",
    ).create_api_gateway_response()

    actual = lambda_handler(stitching_queue_message_event, context)

    assert actual == expected
