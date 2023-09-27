import os
from unittest.mock import patch

import pytest

from handlers.lloyd_george_record_stitch_handler import (
    lambda_handler,
)
from services.dynamo_service import DynamoDBService
from unit.services.test_s3_service import MOCK_PRESIGNED_URL_RESPONSE
from unit.utils.test_order_response_by_filenames import build_dynamo_response_item
from utils.lambda_response import ApiGatewayResponse


def test_throws_error_when_no_nhs_number_supplied(missing_id_event, context):
    actual = lambda_handler(missing_id_event, context)
    expected = ApiGatewayResponse(
        400, "An error occurred due to missing key: 'patientId'", "GET"
    ).create_api_gateway_response()
    assert actual == expected


def test_throws_error_when_environment_variables_not_set(valid_id_event, context):
    actual = lambda_handler(valid_id_event, context)
    expected = ApiGatewayResponse(
        400,
        "An error occurred due to missing key: 'LLOYD_GEORGE_DYNAMODB_NAME'",
        "GET",
    ).create_api_gateway_response()
    assert actual == expected


def test_throws_error_when_nhs_number_not_valid(invalid_id_event, context):
    actual = lambda_handler(invalid_id_event, context)
    expected = ApiGatewayResponse(
        400, f"Invalid NHS number", "GET"
    ).create_api_gateway_response()
    assert actual == expected


def test_throws_error_when_dynamo_service_fails_to_connect(valid_id_event, context):
    os.environ["LLOYD_GEORGE_DYNAMODB_NAME"] = "lg_dynamo"
    os.environ["LLOYD_GEORGE_BUCKET_NAME"] = "lg_bucket"
    actual = lambda_handler(valid_id_event, context)
    expected = ApiGatewayResponse(
        500, f"Unable to retrieve documents for patient 9000000009", "GET"
    ).create_api_gateway_response()
    assert actual == expected


MOCK_LG_DYNAMODB_RESPONSE = {
    "Items": [
        {
            "ID": "uuid_for_page_3",
            "NhsNumber": "1234567890",
            "FileLocation": "s3://ndr-dev-lloyd-george-store/9e9867f0-9767-402d-a4d6-c1af4575a6bf",
            "FileName": "3of3_Lloyd_George_Record_[Joe Bloggs]_[123456789]_[25-12-2019].pdf",
        },
        {
            "ID": "uuid_for_page_1",
            "NhsNumber": "1234567890",
            "FileLocation": "s3://ndr-dev-lloyd-george-store/9e9867f0-9767-402d-a4d6-c1af4575a6bf",
            "FileName": "1of3_Lloyd_George_Record_[Joe Bloggs]_[123456789]_[25-12-2019].pdf",
        },
        {
            "ID": "uuid_for_page_2",
            "NhsNumber": "1234567890",
            "FileLocation": "s3://ndr-dev-lloyd-george-store/9e9867f0-9767-402d-a4d6-c1af4575a6bf",
            "FileName": "2of3_Lloyd_George_Record_[Joe Bloggs]_[123456789]_[25-12-2019].pdf",
        },
    ]
}


@pytest.fixture()
def mock_dynamo_db():
    with patch.object(DynamoDBService, "query_service", return_value=MOCK_LG_DYNAMODB_RESPONSE):
        yield
def test_respond_200_with_presign_url(valid_id_event, context, mock_dynamo_db):
    os.environ["LLOYD_GEORGE_DYNAMODB_NAME"] = "lg_dynamo"
    os.environ["LLOYD_GEORGE_BUCKET_NAME"] = "lg_bucket"

    # some mocking here
    # TODO: mock the s3service as well
    # download_file: dont need return, just dont throw
    # create_download_presigned_url: return mocked presign url response

    actual = lambda_handler(valid_id_event, context)
    expected = ApiGatewayResponse(
        200, MOCK_PRESIGNED_URL_RESPONSE, "GET"
    ).create_api_gateway_response()

    assert actual == expected
