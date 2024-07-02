import pytest
from botocore.exceptions import ClientError
from services.zip_service import DocumentZipService
from utils.lambda_exceptions import GenerateManifestZipException

from ..helpers.data.dynamo_responses import MOCK_SEARCH_RESPONSE


@pytest.fixture
def mock_service(mocker, set_env):
    job_id = "test job id"
    service = DocumentZipService(job_id)
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
    mock_service.dynamo_service.query_all_fields.return_value = dynamo_response

    actual = mock_service.get_zip_trace_item_from_dynamo_by_job_id()

    assert actual == dynamo_response

    mock_service.dynamo_service.query_all_fields.assert_called_with(
        table_name="test_zip_table",
        search_key="JobId",
        search_condition=mock_service.job_id,
    )


def test_get_zip_trace_item_from_dynamo_throws_error_when_boto3_returns_client_error(
    mock_service,
):
    mock_service.dynamo_service.query_all_fields.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "test error"}}, "testing"
    )

    with pytest.raises(GenerateManifestZipException):
        mock_service.get_zip_trace_item_from_dynamo_by_job_id()

    mock_service.dynamo_service.query_all_fields.assert_called_with(
        table_name="test_zip_table",
        search_key="JobId",
        search_condition=mock_service.job_id,
    )
