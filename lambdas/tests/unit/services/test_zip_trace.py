import pytest
from botocore.exceptions import ClientError
from services.zip_service import DocumentZipService
from unit.helpers.data.dynamo_responses import MOCK_SEARCH_RESPONSE
from utils.lambda_exceptions import GenerateManifestZipException


@pytest.fixture
def mock_service(mocker, set_env):
    service = DocumentZipService()
    mocker.patch.object(service, "s3_service")
    mocker.patch.object(service, "dynamo_service")
    yield service


def test_check_number_of_items_from_dynamo_is_one(mock_service):
    items = ["test item"]
    try:
        mock_service.checking_number_of_items_is_one(items)
    except GenerateManifestZipException:
        assert False


@pytest.mark.parametrize("items", [["test item", "another item"], []])
def test_check_number_of_items_throws_error_when_not_one(mock_service, items):

    with pytest.raises(GenerateManifestZipException):
        mock_service.checking_number_of_items_is_one(items)


def test_extract_item_from_dynamo_returns_items(mock_service):

    mock_dynamo_response = {"Items": ["mock items"]}

    actual = mock_service.extract_item_from_dynamo_response(mock_dynamo_response)

    assert actual == ["mock items"]


def test_extract_item_from_dynamo_throws_error_when_no_items(mock_service):

    mock_bad_response = {"nothing": ["nothing"]}

    with pytest.raises(GenerateManifestZipException):
        mock_service.extract_item_from_dynamo_response(mock_bad_response)


def test_get_zip_trace_item_from_dynamo_with_job_id_returns_row(mock_service):
    dynamo_response = MOCK_SEARCH_RESPONSE
    mock_service.dynamo_service.query_with_requested_fields.return_value = (
        dynamo_response
    )
    job_id = "test job id"

    actual = mock_service.get_zip_trace_item_from_dynamo_by_job_id(job_id)

    assert actual == dynamo_response

    mock_service.dynamo_service.query_with_requested_fields.assert_called_with(
        table_name="test_zip_table",
        index_name="JobIdIndex",
        search_key="JobId",
        search_condition=job_id,
    )


def test_get_zip_trace_item_from_dynamo_throws_error_when_boto3_returns_client_error(
    mock_service,
):
    mock_service.dynamo_service.query_with_requested_fields.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "test error"}}, "testing"
    )
    job_id = "test job id"

    with pytest.raises(GenerateManifestZipException):
        mock_service.get_zip_trace_item_from_dynamo_by_job_id(job_id)

    mock_service.dynamo_service.query_with_requested_fields.assert_called_with(
        table_name="test_zip_table",
        index_name="JobIdIndex",
        search_key="JobId",
        search_condition=job_id,
    )
