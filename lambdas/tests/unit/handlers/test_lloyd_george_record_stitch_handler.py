import json
import os
import tempfile

import pytest
from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from enums.trace_status import TraceStatus
from handlers.lloyd_george_record_stitch_handler import (
    create_stitch_job,
    lambda_handler,
)
from models.stitch_trace import DocumentStitchJob
from services.base.s3_service import S3Service
from services.document_service import DocumentService
from tests.unit.conftest import MOCK_LG_BUCKET, TEST_NHS_NUMBER
from tests.unit.helpers.data.test_documents import (
    create_test_lloyd_george_doc_store_refs,
)
from utils.lambda_exceptions import LGStitchServiceException
from utils.lambda_response import ApiGatewayResponse

MOCK_CLIENT_ERROR = ClientError(
    {"Error": {"Code": "500", "Message": "test error"}}, "testing"
)
MOCK_LG_DYNAMODB_RESPONSE_NO_RECORD = {"Items": [], "Count": 0}
MOCK_LLOYD_GEORGE_DOCUMENT_REFS = create_test_lloyd_george_doc_store_refs()
MOCK_STITCHED_FILE = "filename_of_stitched_lg_in_local_storage.pdf"
MOCK_TOTAL_FILE_SIZE = 1024 * 256
MOCK_PRESIGNED_URL = (
    f"https://{MOCK_LG_BUCKET}.s3.amazonaws.com/{TEST_NHS_NUMBER}/abcd-1234-5678"
)
MOCK_STITCH_SERVICE_RESPONSE = DocumentStitchJob(
    jobStatus=TraceStatus.COMPLETED,
    numberOfFiles=3,
    lastUpdated="2023-08-24T14:38:04.095Z",
    presignedUrl=MOCK_PRESIGNED_URL,
    totalFileSizeInBytes=MOCK_TOTAL_FILE_SIZE,
)


@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    monkeypatch.setenv("LLOYD_GEORGE_DYNAMODB_NAME", "mock_dynamodb_table")
    monkeypatch.setenv("LLOYD_GEORGE_BUCKET_NAME", MOCK_LG_BUCKET)
    monkeypatch.setenv("PRESIGNED_ASSUME_ROLE", "mock_role")
    monkeypatch.setenv("CLOUDFRONT_URL", "mock-cloudfront-url.com")


@pytest.fixture
def mock_stitch_service(mocker):
    mocked_class = mocker.patch(
        "handlers.lloyd_george_record_stitch_handler.LloydGeorgeStitchJobService"
    )
    mocked_service = mocked_class.return_value
    yield mocked_service


@pytest.fixture
def fetch_available_document_references_by_type(mocker):
    mocked_method = mocker.patch.object(
        DocumentService, "fetch_available_document_references_by_type"
    )
    mocked_method.return_value = MOCK_LLOYD_GEORGE_DOCUMENT_REFS
    yield mocked_method


@pytest.fixture
def mock_s3(mocker):
    mocked_instance = mocker.patch(
        "services.lloyd_george_stitch_service.S3Service", spec=S3Service
    ).return_value
    mocked_instance.create_download_presigned_url.return_value = MOCK_PRESIGNED_URL
    yield mocked_instance


@pytest.fixture
def mock_stitch_pdf(mocker):
    yield mocker.patch(
        "services.lloyd_george_stitch_service.stitch_pdf",
        return_value=MOCK_STITCHED_FILE,
    )


@pytest.fixture
def mock_tempfile(mocker):
    yield mocker.patch.object(tempfile, "mkdtemp", return_value="/tmp/")


@pytest.fixture
def joe_bloggs_event():
    api_gateway_proxy_event = {
        "httpMethod": "POST",
        "queryStringParameters": {"patientId": TEST_NHS_NUMBER},
    }
    return api_gateway_proxy_event


def test_lambda_handler_respond_with_200_and_presign_url(
    valid_id_event_without_auth_header, context, mocker, set_env
):
    expected_response_object = {
        "jobStatus": "Completed",
        "presignedUrl": MOCK_PRESIGNED_URL,
        "numberOfFiles": 3,
        "lastUpdated": "2023-08-24T14:38:04.095Z",
        "totalFileSizeInBytes": MOCK_TOTAL_FILE_SIZE,
    }
    expected = ApiGatewayResponse(
        200, json.dumps(expected_response_object), "GET"
    ).create_api_gateway_response()

    mock_create_stitch_job = mocker.patch(
        "handlers.lloyd_george_record_stitch_handler.get_stitch_job",
        return_value=expected,
    )
    actual = lambda_handler(valid_id_event_without_auth_header, context)

    assert actual == expected

    mock_create_stitch_job.assert_called_once()


def test_lambda_handler_respond_create_new_job(
    valid_id_post_event_with_auth_header, context, mock_stitch_service, mocker, set_env
):
    expected_response_object = {
        "jobStatus": TraceStatus.PENDING,
    }
    expected = ApiGatewayResponse(
        200, json.dumps(expected_response_object), "POST"
    ).create_api_gateway_response()

    mock_create_stitch_job = mocker.patch(
        "handlers.lloyd_george_record_stitch_handler.create_stitch_job",
        return_value=expected,
    )

    actual = lambda_handler(valid_id_post_event_with_auth_header, context)

    assert actual == expected
    mock_create_stitch_job.assert_called_once()


def test_lambda_handler_respond_400_when_no_nhs_number_supplied(
    missing_id_event, context, set_env
):
    actual = lambda_handler(missing_id_event, context)

    expected_body = json.dumps(
        {
            "message": "An error occurred due to missing key",
            "err_code": "PN_4002",
            "interaction_id": "88888888-4444-4444-4444-121212121212",
        }
    )
    expected = ApiGatewayResponse(
        400, expected_body, "GET"
    ).create_api_gateway_response()
    assert actual == expected


def test_lambda_handler_respond_500_when_environment_variables_not_set(
    joe_bloggs_event, context
):
    os.environ.pop("CLOUDFRONT_URL", None)

    actual = lambda_handler(joe_bloggs_event, context)

    expected_body = json.dumps(
        {
            "message": "An error occurred due to missing environment variable: 'CLOUDFRONT_URL'",
            "err_code": "ENV_5001",
            "interaction_id": "88888888-4444-4444-4444-121212121212",
        }
    )
    expected = ApiGatewayResponse(
        500,
        expected_body,
        "POST",
    ).create_api_gateway_response()
    assert actual == expected


def test_lambda_handler_respond_400_when_nhs_number_not_valid(
    invalid_id_event, context, set_env
):
    actual = lambda_handler(invalid_id_event, context)

    nhs_number = invalid_id_event["queryStringParameters"]["patientId"]
    expected_body = json.dumps(
        {
            "message": f"Invalid patient number {nhs_number}",
            "err_code": "PN_4001",
            "interaction_id": "88888888-4444-4444-4444-121212121212",
        }
    )
    expected = ApiGatewayResponse(
        400, expected_body, "GET"
    ).create_api_gateway_response()
    assert actual == expected


def test_lambda_handler_respond_500_when_failed_to_retrieve_lg_record(
    joe_bloggs_event, mocker, context, set_env
):
    mocker.patch(
        "handlers.lloyd_george_record_stitch_handler.create_stitch_job",
        side_effect=LGStitchServiceException(500, LambdaError.StitchNoService),
    )

    actual = lambda_handler(joe_bloggs_event, context)

    expected = ApiGatewayResponse(
        500,
        LambdaError.StitchNoService.create_error_body(),
        "POST",
    ).create_api_gateway_response()

    assert actual == expected


def test_lambda_handler_respond_404_throws_error_when_no_lloyd_george_for_patient_in_record(
    valid_id_post_event_with_auth_header,
    context,
    fetch_available_document_references_by_type,
    mocker,
    set_env,
):
    mocker.patch(
        "handlers.lloyd_george_record_stitch_handler.create_stitch_job",
        side_effect=LGStitchServiceException(404, LambdaError.StitchNotFound),
    )

    actual = lambda_handler(valid_id_post_event_with_auth_header, context)

    expected_body = json.dumps(
        {
            "message": "Lloyd george record not found for patient",
            "err_code": "LGS_4001",
            "interaction_id": "88888888-4444-4444-4444-121212121212",
        }
    )
    expected = ApiGatewayResponse(
        404,
        expected_body,
        "POST",
    ).create_api_gateway_response()
    assert actual == expected


def test_create_stitch_job_respond_create_new_job(
    valid_id_post_event_with_auth_header, context, mock_stitch_service, set_env
):
    mock_stitch_service.get_or_create_stitch_job.return_value = TraceStatus.PENDING
    expected_response_object = {
        "jobStatus": "Pending",
    }
    expected = ApiGatewayResponse(
        200, json.dumps(expected_response_object), "POST"
    ).create_api_gateway_response()

    actual = create_stitch_job(valid_id_post_event_with_auth_header, context)

    assert actual == expected

    mock_stitch_service.query_document_stitch_job.assert_not_called()
    mock_stitch_service.get_or_create_stitch_job.assert_called_with(TEST_NHS_NUMBER)


def test_get_stitch_job_respond_with_200_and_presign_url(
    valid_id_event_without_auth_header, context, set_env, mock_stitch_service
):
    mock_stitch_service.query_document_stitch_job.return_value = (
        MOCK_STITCH_SERVICE_RESPONSE
    )
    expected_response_object = {
        "jobStatus": "Completed",
        "presignedUrl": MOCK_PRESIGNED_URL,
        "numberOfFiles": 3,
        "lastUpdated": "2023-08-24T14:38:04.095Z",
        "totalFileSizeInBytes": MOCK_TOTAL_FILE_SIZE,
    }
    expected = ApiGatewayResponse(
        200, json.dumps(expected_response_object), "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_event_without_auth_header, context)

    assert actual == expected

    mock_stitch_service.query_document_stitch_job.assert_called_once()
