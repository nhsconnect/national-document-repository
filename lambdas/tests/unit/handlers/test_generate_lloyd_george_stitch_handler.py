import pytest
from enums.lambda_error import LambdaError
from enums.trace_status import TraceStatus
from handlers.generate_lloyd_george_stitch_handler import (
    lambda_handler,
    prepare_stitch_trace_data,
    stitch_record_handler,
)
from tests.unit.conftest import TEST_NHS_NUMBER, TEST_UUID
from utils.lambda_exceptions import LGStitchServiceException
from utils.lambda_response import ApiGatewayResponse

INVALID_EVENT_EXAMPLE = {
    "Records": [
        {
            "eventID": "1",
            "eventName": "INSERT",
            "eventVersion": "1.0",
            "eventSource": "aws:dynamodb",
            "awsRegion": "us-east-1",
            "dynamodb": {
                "Keys": {"Id": {"N": "101"}},
                "SequenceNumber": "111",
                "SizeBytes": 26,
                "StreamViewType": "NEW_AND_OLD_IMAGES",
            },
            "eventSourceARN": "stream-ARN",
        }
    ],
}

VALID_NEW_IMAGE = {
    "NhsNumber": {"S": f"{TEST_NHS_NUMBER}"},
    "Status": {"S": TraceStatus.PENDING},
    "ID": {"S": f"{TEST_UUID}"},
    "Created": {"S": "2023-07-02T13:11:00.544608Z"},
    "ExpireAt": {"S": "9999999"},
}

MODIFY_EVENT_EXAMPLE = {
    "Records": [
        {
            "eventID": "1",
            "eventName": "MODIFY",
            "eventVersion": "1.0",
            "eventSource": "aws:dynamodb",
            "awsRegion": "us-east-1",
            "dynamodb": {
                "Keys": {"Id": {"N": "101"}},
                "NewImage": VALID_NEW_IMAGE,
                "SequenceNumber": "111",
                "SizeBytes": 26,
                "StreamViewType": "NEW_AND_OLD_IMAGES",
            },
            "eventSourceARN": "stream-ARN",
        }
    ],
}


MOCK_EVENT_RESPONSE = {
    "Records": [
        {
            "eventName": "INSERT",
            "dynamodb": {
                "NewImage": VALID_NEW_IMAGE,
            },
        }
    ]
}

INVALID_IMAGE = {
    "Status": {"S": "Pending"},
    "ID": {"S": f"{TEST_UUID}"},
    "Created": {"S": "2023-07-02T13:11:00.544608Z"},
}

PROCESSES_VALID_IMAGE = {
    "NhsNumber": TEST_NHS_NUMBER,
    "Status": TraceStatus.PENDING,
    "ID": TEST_UUID,
    "Created": "2023-07-02T13:11:00.544608Z",
    "ExpireAt": "9999999",
}

NEW_IMAGE_NOT_DICT_EXAMPLE = {
    "Records": [
        {
            "eventID": "1",
            "eventName": "INSERT",
            "eventVersion": "1.0",
            "eventSource": "aws:dynamodb",
            "awsRegion": "us-east-1",
            "dynamodb": {
                "Keys": {"Id": {"N": "101"}},
                "NewImage": ["hello"],
                "SequenceNumber": "111",
                "SizeBytes": 26,
                "StreamViewType": "NEW_AND_OLD_IMAGES",
            },
            "eventSourceARN": "stream-ARN",
        }
    ],
}


@pytest.fixture
def mock_lloyd_george_generate_stitch_service(mocker):
    mock_object = mocker.MagicMock()
    mocker.patch(
        "handlers.generate_lloyd_george_stitch_handler.LloydGeorgeStitchService",
        return_value=mock_object,
    )
    yield mock_object


def test_handler_200_response_no_issues(context, set_env, mocker):
    expected = ApiGatewayResponse(200, "", "GET").create_api_gateway_response()
    mock_stitch_record_handler = mocker.patch(
        "handlers.generate_lloyd_george_stitch_handler.stitch_record_handler"
    )
    mock_prepare_stitch_trace_data = mocker.patch(
        "handlers.generate_lloyd_george_stitch_handler.prepare_stitch_trace_data"
    )

    actual = lambda_handler(MOCK_EVENT_RESPONSE, context)

    assert expected == actual
    mock_stitch_record_handler.assert_called_once()
    mock_prepare_stitch_trace_data.assert_called_once()


def test_400_response_thrown_if_no_records_in_event(context, set_env):
    actual = lambda_handler({}, context)
    expected = ApiGatewayResponse(
        400, LambdaError.StitchClient.create_error_body(), "GET"
    ).create_api_gateway_response()

    assert expected == actual


def test_400_response_thrown_if_no_new_trace_in_image(context, set_env):
    actual = lambda_handler(INVALID_EVENT_EXAMPLE, context)
    expected = ApiGatewayResponse(
        400, LambdaError.StitchClient.create_error_body(), "GET"
    ).create_api_gateway_response()

    assert expected == actual


def test_400_response_if_event_name_not_insert(context, set_env):
    actual = lambda_handler(MODIFY_EVENT_EXAMPLE, context)
    expected = ApiGatewayResponse(
        400, LambdaError.StitchClient.create_error_body(), "GET"
    ).create_api_gateway_response()

    assert expected == actual


def test_400_response_if_new_image_is_not_dictionary(context, set_env):
    actual = lambda_handler(NEW_IMAGE_NOT_DICT_EXAMPLE, context)
    expected = ApiGatewayResponse(
        400, LambdaError.StitchClient.create_error_body(), "GET"
    ).create_api_gateway_response()

    assert expected == actual


def test_handler_return_500_response_when_stitch_record_error(context, set_env, mocker):
    mocker.patch(
        "handlers.generate_lloyd_george_stitch_handler.stitch_record_handler",
        side_effect=LGStitchServiceException(500, LambdaError.MockError),
    )
    mocker.patch(
        "handlers.generate_lloyd_george_stitch_handler.prepare_stitch_trace_data"
    )

    actual = lambda_handler(MOCK_EVENT_RESPONSE, context)

    expected = ApiGatewayResponse(
        500, LambdaError.MockError.create_error_body(), "GET"
    ).create_api_gateway_response()

    assert expected == actual


def test_stitch_record_handler_raise_error_if_zip_trace_model_validation_fails(
    mock_lloyd_george_generate_stitch_service,
):
    with pytest.raises(LGStitchServiceException):
        stitch_record_handler(INVALID_IMAGE)

    mock_lloyd_george_generate_stitch_service.assert_not_called()


def test_stitch_record_handler_happy_path(
    mock_lloyd_george_generate_stitch_service,
):
    stitch_record_handler(PROCESSES_VALID_IMAGE)

    mock_lloyd_george_generate_stitch_service.handle_stitch_request.assert_called_once()


def test_zip_service_handle_stitch_request_called(
    mock_lloyd_george_generate_stitch_service,
):
    mock_lloyd_george_generate_stitch_service.handle_stitch_request.side_effect = (
        LGStitchServiceException("test", LambdaError.MockError)
    )

    with pytest.raises(LGStitchServiceException):
        stitch_record_handler(PROCESSES_VALID_IMAGE)

    mock_lloyd_george_generate_stitch_service.handle_stitch_request.assert_called_once()


def test_prepare_stitch_trace_data():
    actual = prepare_stitch_trace_data(VALID_NEW_IMAGE)
    expected = PROCESSES_VALID_IMAGE

    assert actual == expected
