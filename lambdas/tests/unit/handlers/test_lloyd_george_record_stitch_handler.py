from unittest.mock import patch

import pypdf.errors
import pytest
from botocore.exceptions import ClientError

from handlers.lloyd_george_record_stitch_handler import lambda_handler
from services.dynamo_service import DynamoDBService
from tests.unit.services.test_s3_service import MOCK_PRESIGNED_URL_RESPONSE
from tests.unit.conftest import MOCK_LG_BUCKET
from utils.lambda_response import ApiGatewayResponse


def test_respond_200_with_presign_url(
    valid_id_event, context, set_env, mock_dynamo_db, mock_s3, mock_stitch_pdf
):
    actual = lambda_handler(valid_id_event, context)
    expected = ApiGatewayResponse(
        200, MOCK_PRESIGNED_URL_RESPONSE, "GET"
    ).create_api_gateway_response()

    assert actual == expected


def test_aws_services_are_correctly_called(
    valid_id_event, context, set_env, mock_dynamo_db, mock_s3, mock_stitch_pdf
):
    lambda_handler(valid_id_event, context)

    mock_dynamo_db.assert_called_once()

    for mock_record in MOCK_LG_DYNAMODB_RESPONSE["Items"]:
        s3_key = mock_record["ID"]
        local_filename = "/tmp/" + mock_record["FileName"]
        mock_s3.download_file.assert_any_call(MOCK_LG_BUCKET, s3_key, local_filename)

    mock_s3.upload_file_with_tags.assert_called_with(
        file_key="Combined_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf",
        file_name=MOCK_STITCHED_FILE,
        s3_bucket_name=MOCK_LG_BUCKET,
        tags={"auto_delete": "true"},
    )


def test_respond_400_throws_error_when_no_nhs_number_supplied(
    missing_id_event, context
):
    actual = lambda_handler(missing_id_event, context)
    expected = ApiGatewayResponse(
        400, "An error occurred due to missing key: 'patientId'", "GET"
    ).create_api_gateway_response()
    assert actual == expected


def test_respond_500_throws_error_when_environment_variables_not_set(
    valid_id_event, context
):
    actual = lambda_handler(valid_id_event, context)
    expected = ApiGatewayResponse(
        500,
        "An error occurred due to missing key: 'LLOYD_GEORGE_DYNAMODB_NAME'",
        "GET",
    ).create_api_gateway_response()
    assert actual == expected


def test_respond_400_throws_error_when_nhs_number_not_valid(invalid_id_event, context):
    actual = lambda_handler(invalid_id_event, context)
    expected = ApiGatewayResponse(
        400, "Invalid NHS number", "GET"
    ).create_api_gateway_response()
    assert actual == expected


def test_respond_500_throws_error_when_dynamo_service_fails_to_connect(
    valid_id_event, context, set_env, mock_dynamo_db
):
    mock_dynamo_db.side_effect = MOCK_CLIENT_ERROR
    actual = lambda_handler(valid_id_event, context)
    expected = ApiGatewayResponse(
        500, "Unable to retrieve documents for patient 9000000009", "GET"
    ).create_api_gateway_response()
    assert actual == expected


def test_respond_500_throws_error_when_fail_to_download_lloyd_george_file(
    valid_id_event, context, set_env, mock_dynamo_db, mock_s3
):
    mock_s3.download_file.side_effect = MOCK_CLIENT_ERROR
    actual = lambda_handler(valid_id_event, context)
    expected = ApiGatewayResponse(
        500, "Unable to retrieve documents for patient 9000000009", "GET"
    ).create_api_gateway_response()
    assert actual == expected


def test_respond_404_throws_error_when_no_lloyd_george_for_patient_in_record(
    valid_id_event, context, set_env, mock_dynamo_db
):
    mock_dynamo_db.return_value = MOCK_LG_DYNAMODB_RESPONSE_NO_RECORD
    actual = lambda_handler(valid_id_event, context)
    expected = ApiGatewayResponse(
        404, "Lloyd george record not found for patient 9000000009", "GET"
    ).create_api_gateway_response()
    assert actual == expected


def test_respond_500_throws_error_when_fail_to_stitch_lloyd_george_file(
    valid_id_event, context, set_env, mock_dynamo_db, mock_s3, mock_stitch_pdf
):
    mock_stitch_pdf.side_effect = pypdf.errors.ParseError

    actual = lambda_handler(valid_id_event, context)
    expected = ApiGatewayResponse(
        500, "Unable to return stitched pdf file due to internal error", "GET"
    ).create_api_gateway_response()
    assert actual == expected


def test_respond_500_throws_error_when_fail_to_upload_lloyd_george_file(
    valid_id_event, context, set_env, mock_dynamo_db, mock_s3, mock_stitch_pdf
):
    mock_s3.upload_file_with_tags.side_effect = MOCK_CLIENT_ERROR
    actual = lambda_handler(valid_id_event, context)
    expected = ApiGatewayResponse(
        500, "Unexpected error when uploading Lloyd George record", "GET"
    ).create_api_gateway_response()
    assert actual == expected


MOCK_CLIENT_ERROR = ClientError(
    {"Error": {"Code": "500", "Message": "test error"}}, "testing"
)

MOCK_LG_DYNAMODB_RESPONSE_NO_RECORD = {"Items": [], "Count": 0}

MOCK_LG_DYNAMODB_RESPONSE = {
    "Items": [
        {
            "ID": "uuid_for_page_3",
            "NhsNumber": "1234567890",
            "FileLocation": "s3://ndr-dev-lloyd-george-store/9e9867f0-9767-402d-a4d6-c1af4575a6bf",
            "FileName": "3of3_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf",
        },
        {
            "ID": "uuid_for_page_1",
            "NhsNumber": "1234567890",
            "FileLocation": "s3://ndr-dev-lloyd-george-store/9e9867f0-9767-402d-a4d6-c1af4575a6bf",
            "FileName": "1of3_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf",
        },
        {
            "ID": "uuid_for_page_2",
            "NhsNumber": "1234567890",
            "FileLocation": "s3://ndr-dev-lloyd-george-store/9e9867f0-9767-402d-a4d6-c1af4575a6bf",
            "FileName": "2of3_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf",
        },
    ]
}

MOCK_STITCHED_FILE = "filename_of_stitched_lg_in_local_storage.pdf"


# @pytest.fixture
# def patch_env_vars():
#     patched_env_vars = {
#         "LLOYD_GEORGE_DYNAMODB_NAME": "lg_dynamo",
#         "LLOYD_GEORGE_BUCKET_NAME": "lg_bucket",
#     }
#     with patch.dict(os.environ, patched_env_vars):
#         yield patched_env_vars


@pytest.fixture
def mock_dynamo_db():
    with patch.object(DynamoDBService, "query_service") as mocked_query_service:
        mocked_query_service.return_value = MOCK_LG_DYNAMODB_RESPONSE
        yield mocked_query_service


@pytest.fixture
def mock_s3():
    with patch("handlers.lloyd_george_record_stitch_handler.S3Service") as mock_class:
        mock_s3_service_instance = mock_class.return_value
        mock_s3_service_instance.create_download_presigned_url.return_value = (
            MOCK_PRESIGNED_URL_RESPONSE
        )
        yield mock_s3_service_instance


@pytest.fixture
def mock_stitch_pdf():
    with patch(
        "handlers.lloyd_george_record_stitch_handler.stitch_pdf"
    ) as mocked_stitch_pdf:
        mocked_stitch_pdf.return_value = MOCK_STITCHED_FILE
        yield mocked_stitch_pdf
