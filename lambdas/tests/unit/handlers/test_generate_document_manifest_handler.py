import pytest
from enums.lambda_error import LambdaError
from handlers.generate_document_manifest_handler import (
    lambda_handler,
    manifest_zip_handler,
    prepare_zip_trace_data,
)
from tests.unit.conftest import TEST_DOCUMENT_LOCATION, TEST_FILE_NAME, TEST_UUID
from utils.lambda_exceptions import DocumentManifestServiceException
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
    "FilesToDownload": {
        "M": {
            f"{TEST_DOCUMENT_LOCATION}1": {"S": f"{TEST_FILE_NAME}1"},
            f"{TEST_DOCUMENT_LOCATION}2": {"S": f"{TEST_FILE_NAME}2"},
        }
    },
    "Status": {"S": "Pending"},
    "ID": {"S": f"{TEST_UUID}"},
    "JobId": {"S": f"{TEST_UUID}"},
    "Created": {"S": "2023-07-02T13:11:00.544608Z"},
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
    "FilesToDownload": {
        f"{TEST_DOCUMENT_LOCATION}1": f"{TEST_FILE_NAME}1",
        f"{TEST_DOCUMENT_LOCATION}2": f"{TEST_FILE_NAME}2",
    },
    "Status": "Pending",
    "ID": TEST_UUID,
    "JobId": TEST_UUID,
    "Created": "2023-07-02T13:11:00.544608Z",
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
def mock_document_manifest_zip_service(mocker):
    mock_object = mocker.MagicMock()
    mocker.patch(
        "handlers.generate_document_manifest_handler.DocumentManifestZipService",
        return_value=mock_object,
    )
    yield mock_object


def test_handler_200_response_no_issues(context, set_env, mocker):
    expected = ApiGatewayResponse(200, "", "GET").create_api_gateway_response()
    mock_manifest_zip_handler = mocker.patch(
        "handlers.generate_document_manifest_handler.manifest_zip_handler"
    )
    mock_prepare_zip_trace_data = mocker.patch(
        "handlers.generate_document_manifest_handler.prepare_zip_trace_data"
    )

    actual = lambda_handler(MOCK_EVENT_RESPONSE, context)

    assert expected == actual
    mock_manifest_zip_handler.assert_called_once()
    mock_prepare_zip_trace_data.assert_called_once()


def test_400_response_thrown_if_no_records_in_event(context, set_env):
    expected = ApiGatewayResponse(400, "", "GET").create_api_gateway_response()
    actual = lambda_handler({}, context)
    assert expected == actual


def test_400_response_thrown_if_no_new_zip_trace_in_image(context, set_env):
    expected = ApiGatewayResponse(400, "", "GET").create_api_gateway_response()
    actual = lambda_handler(INVALID_EVENT_EXAMPLE, context)
    assert expected == actual


def test_400_response_if_event_name_not_insert(context, set_env):
    expected = ApiGatewayResponse(400, "", "GET").create_api_gateway_response()
    actual = lambda_handler(MODIFY_EVENT_EXAMPLE, context)
    assert expected == actual


def test_400_response_if_new_image_is_not_dictionary(context, set_env):
    expected = ApiGatewayResponse(400, "", "GET").create_api_gateway_response()
    actual = lambda_handler(NEW_IMAGE_NOT_DICT_EXAMPLE, context)
    assert expected == actual


def test_handler_return_500_response_when_manifest_zip_error(context, set_env, mocker):
    mocker.patch(
        "handlers.generate_document_manifest_handler.manifest_zip_handler",
        side_effect=DocumentManifestServiceException(500, LambdaError.MockError),
    )
    mocker.patch("handlers.generate_document_manifest_handler.prepare_zip_trace_data")

    actual = lambda_handler(MOCK_EVENT_RESPONSE, context)

    expected = ApiGatewayResponse(
        500, LambdaError.MockError.create_error_body(), "GET"
    ).create_api_gateway_response()

    assert expected == actual


def test_manifest_zip_handler_raise_error_if_zip_trace_model_validation_fails(
    mock_document_manifest_zip_service,
):
    with pytest.raises(DocumentManifestServiceException):
        manifest_zip_handler(INVALID_IMAGE)

    mock_document_manifest_zip_service.assert_not_called()


def test_manifest_zip_handler_happy_path(
    mock_document_manifest_zip_service,
):
    manifest_zip_handler(PROCESSES_VALID_IMAGE)

    mock_document_manifest_zip_service.handle_zip_request.assert_called_once()


def test_zip_service_handle_zip_request_called(mock_document_manifest_zip_service):
    mock_document_manifest_zip_service.handle_zip_request.side_effect = (
        DocumentManifestServiceException("test", LambdaError.MockError)
    )

    with pytest.raises(DocumentManifestServiceException):
        manifest_zip_handler(PROCESSES_VALID_IMAGE)

    mock_document_manifest_zip_service.handle_zip_request.assert_called_once()


def test_prepare_zip_trace_data():
    actual = prepare_zip_trace_data(VALID_NEW_IMAGE)
    expected = PROCESSES_VALID_IMAGE

    assert actual == expected
