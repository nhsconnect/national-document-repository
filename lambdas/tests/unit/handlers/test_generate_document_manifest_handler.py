import pytest
from enums.lambda_error import LambdaError
from handlers.generate_document_manifest_handler import (
    lambda_handler,
    manifest_zip_handler,
)
from unit.conftest import TEST_DOCUMENT_LOCATION, TEST_FILE_NAME, TEST_UUID
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
                "NewImage": {"hello"},
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


@pytest.fixture
def mock_document_manifest_zip_service(mocker):
    mock_object = mocker.MagicMock()
    mocker.patch(
        "handlers.generate_document_manifest_handler.DocumentManifestZipService",
        return_value=mock_object,
    )
    yield mock_object


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


def test_manifest_zip_handler_raise_error_if_zip_trace_model_validation_fails(
    mock_document_manifest_zip_service,
):
    with pytest.raises(DocumentManifestServiceException):
        manifest_zip_handler(INVALID_IMAGE)

    mock_document_manifest_zip_service.assert_not_called()


def test_manifest_zip_handler_happy_path(
    mock_document_manifest_zip_service,
):
    manifest_zip_handler(VALID_NEW_IMAGE)

    mock_document_manifest_zip_service.assert_called_once()


def test_zip_service_handle_zip_request_called(mock_document_manifest_zip_service):
    mock_document_manifest_zip_service.handle_zip_request.side_effect = (
        DocumentManifestServiceException("test", LambdaError.MockError)
    )

    with pytest.raises(DocumentManifestServiceException):
        manifest_zip_handler(VALID_NEW_IMAGE)

    mock_document_manifest_zip_service.assert_called_once()
    mock_document_manifest_zip_service.handle_zip_request.assert_called_once()


def test_200_response_no_issues():
    pass


def test_prepare_zip_trace_data():
    pass

    # # def test_upload_zip_file(mock_service):
    # #     f"patient-record-{zip_trace.job_id}.zip"
    # def test_remove_temp_files(mock_service):
    #     mock_service.remove_temp_files()
    #
    #     assert mock_service.temp_output_dir == None
    #     assert mock_service.temp_zip_trace == None
    #
    #
    # def test_check_number_of_items_from_dynamo_is_one(mock_service):
    #     items = ["test item"]
    #     try:
    #         mock_service.checking_number_of_items_is_one(items)
    #     except GenerateManifestZipException:
    #         assert False
    #
    #
    # @pytest.mark.parametrize("items", [["test item", "another item"], []])
    # def test_check_number_of_items_throws_error_when_not_one(mock_service, items):
    #
    #     with pytest.raises(GenerateManifestZipException):
    #         mock_service.checking_number_of_items_is_one(items)
    #
    #
    # def test_extract_item_from_dynamo_returns_items(mock_service):
    #
    #     mock_dynamo_response = {"Items": ["mock items"]}
    #
    #     actual = mock_service.extract_item_from_dynamo_response(mock_dynamo_response)
    #
    #     assert actual == ["mock items"]
    #
    #
    # def test_extract_item_from_dynamo_throws_error_when_no_items(mock_service):
    #
    #     mock_bad_response = {"nothing": ["nothing"]}
    #
    #     with pytest.raises(GenerateManifestZipException):
    #         mock_service.extract_item_from_dynamo_response(mock_bad_response)
    #
    #
    # def test_get_zip_trace_item_from_dynamo_with_job_id_returns_row(mock_service):
    #     dynamo_response = MOCK_SEARCH_RESPONSE
    #     mock_service.dynamo_service.query_all_fields.return_value = dynamo_response
    #
    #     actual = mock_service.get_zip_trace_item_from_dynamo_by_job_id()
    #
    #     assert actual == dynamo_response
    #
    #     mock_service.dynamo_service.query_all_fields.assert_called_with(
    #         table_name="test_zip_table",
    #         search_key="JobId",
    #         search_condition=mock_service.job_id,
    #     )
    #
    #
    # def test_get_zip_trace_item_from_dynamo_throws_error_when_boto3_returns_client_error(
    #     mock_service,
    # ):
    #     mock_service.dynamo_service.query_all_fields.side_effect = ClientError(
    #         {"Error": {"Code": "500", "Message": "test error"}}, "testing"
    #     )
    #
    #     with pytest.raises(GenerateManifestZipException):
    #         mock_service.get_zip_trace_item_from_dynamo_by_job_id()
    #
    #     mock_service.dynamo_service.query_all_fields.assert_called_with(
    #         table_name="test_zip_table",
    #         search_key="JobId",
    #         search_condition=mock_service.job_id,
    #     )
