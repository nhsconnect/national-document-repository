import pytest
from enums.lambda_error import LambdaError
from handlers.pdf_stitching_handler import lambda_handler
from models.sqs.pdf_stitching_sqs_message import PdfStitchingSqsMessage
from services.pdf_stitching_service import PdfStitchingService
from tests.unit.conftest import MOCK_INTERACTION_ID, TEST_NHS_NUMBER
from tests.unit.helpers.data.sqs.test_messages import (
    no_body_message_event,
    stitching_queue_message_event,
)
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


@pytest.mark.parametrize("invalid_event", [{}, {"Records": []}, no_body_message_event])
def test_handler_handles_invalid_events(mock_process_message, invalid_event, context):
    request_context.request_id = MOCK_INTERACTION_ID
    expected = ApiGatewayResponse(
        status_code=400,
        body=LambdaError.SqsInvalidEvent.create_error_body(),
        methods="GET",
    ).create_api_gateway_response()

    actual = lambda_handler(invalid_event, context)

    assert actual == expected
    mock_process_message.assert_not_called()
