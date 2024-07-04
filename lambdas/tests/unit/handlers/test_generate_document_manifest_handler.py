import pytest
from handlers.generate_document_manifest_handler import lambda_handler
from services.document_manifest_zip_service import DocumentManifestZipService
from unit.services.test_document_manifest_zip_service import TEST_ZIP_TRACE
from utils.lambda_response import ApiGatewayResponse

EVENT_EXAMPLE = {
    "eventID": "1",
    "eventName": "INSERT",
    "eventVersion": "1.0",
    "eventSource": "aws:dynamodb",
    "awsRegion": "us-east-1",
    "dynamodb": {
        "Keys": {"Id": {"N": "101"}},
        "NewImage": {"Message": {"S": "New item!"}, "Id": {"N": "101"}},
        "SequenceNumber": "111",
        "SizeBytes": 26,
        "StreamViewType": "NEW_AND_OLD_IMAGES",
    },
    "eventSourceARN": "stream-ARN",
}

MOCK_EVENT_RESPONSE = {
    "Records": [
        {
            "eventID": "402bad225401dc8f7306d76e26be7c50",
            "eventName": "INSERT",
            "eventVersion": "1.1",
            "eventSource": "aws:dynamodb",
            "awsRegion": "eu-west-2",
            "dynamodb": {
                "ApproximateCreationDateTime": 1719934814.0,
                "Keys": {"ID": {"S": "37d79b0e-31f6-49d9-b882-b3d2c8308b2c"}},
                "NewImage": {
                    "FilesToDownload": {
                        "M": {
                            "s3://ndrc-lloyd-george-store/9000000004/f2a8e23d-80b1-4682-9ccb-ee84d65b6937": {
                                "S": "1of5_Lloyd_George_Record_[Jane Smith]_[9000000004]_[22-10-2010].pdf"
                            },
                            "s3://ndrc-lloyd-george-store/9000000004/aefbfb37-6e52-4def-a772-6165376637b1": {
                                "S": "1of5_Lloyd_George_Record_[Jane Smith]_[9000000004]_[22-10-2010](2).pdf"
                            },
                        }
                    },
                    "Status": {"S": "Pending"},
                    "ZipFileLocation": {
                        "S": "s3://ndrc-zip-request-store/e9653b17-203f-4a9b-81b5-1cb71eb10423"
                    },
                    "ID": {"S": "37d79b0e-31f6-49d9-b882-b3d2c8308b2c"},
                    "JobId": {"S": "39653b17-203f-4a9b-81b5-1cb71eb10423"},
                    "Created": {"S": "2023-07-02T13:11:00.544608Z"},
                },
                "SequenceNumber": "837800000000009615266796",
                "SizeBytes": 552,
                "StreamViewType": "NEW_AND_OLD_IMAGES",
            },
            "eventSourceARN": "arn:aws:dynamodb:eu-west-2:11111111111111:table"
            "/ndrc_ZipStoreReferenceMetadata/stream/2024-07-02T08:32:50.481",
        }
    ]
}


@pytest.fixture
def mock_document_manifest_zip_service(mocker):
    service = DocumentManifestZipService(TEST_ZIP_TRACE)
    mocker.patch.object(service, "s3_service")
    mocker.patch.object(service, "dynamo_service")
    yield service


def test_400_response_thrown_if_no_records_in_event(missing_id_event, context):

    expected = ApiGatewayResponse(400, "", "GET").create_api_gateway_response()
    actual = lambda_handler(EVENT_EXAMPLE, context)
    # assert True
    assert expected == actual


def test_400_response_thrown_if_no_new_zip_trace_in_image():
    pass


def test_400_response_if_event_name_not_insert():
    pass


def test_500_response_if_zip_trace_model_validation_fails():
    pass


def test_zip_service_handle_zip_request_called():
    pass


def test_200_response_no_issues():
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
