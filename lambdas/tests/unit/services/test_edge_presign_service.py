import hashlib
from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from services.edge_presign_service import EdgePresignService
from utils.lambda_exceptions import CloudFrontEdgeException


# Fixture that patches SSMService and DynamoDBService for all tests
@pytest.fixture
@patch("services.edge_presign_service.SSMService")
@patch("services.edge_presign_service.DynamoDBService")
def edge_presign_service(mock_dynamo_service, mock_ssm_service):
    # Mock SSM parameter retrieval
    mock_ssm_service.return_value.get_ssm_parameter.return_value = "Mocked_Table_Name"
    # Configure DynamoDB mock behavior for each test
    mock_dynamo_service.return_value.update_item.return_value = None
    return EdgePresignService()


@pytest.fixture
def request_values():
    return {
        "uri": "/some/path",
        "querystring": "X-Amz-Algorithm=algo&X-Amz-Credential=cred&X-Amz-Date=date&X-Amz-Expires=3600",
        "domain_name": "example-lloyd.com",
    }


def test_use_presign(edge_presign_service, request_values):
    with patch.object(
        edge_presign_service, "attempt_presign_ingestion"
    ) as mock_attempt_presign_ingestion:
        edge_presign_service.use_presign(request_values)

        # Check that the MD5 hash was created and passed to attempt_presign_ingestion correctly
        expected_hash = hashlib.md5(
            f"{request_values['uri']}?{request_values['querystring']}".encode("utf-8")
        ).hexdigest()
        mock_attempt_presign_ingestion.assert_called_once_with(
            uri_hash=expected_hash, domain_name="example-lloyd.com"
        )


def test_attempt_presign_ingestion_success(edge_presign_service):
    # Call the method, expecting no exceptions
    edge_presign_service.attempt_presign_ingestion("hashed_uri", "test-lloyd.com")


def test_attempt_presign_ingestion_client_error(edge_presign_service):
    # Mock DynamoDB's update_item to raise a ClientError
    client_error = ClientError(
        {"Error": {"Code": "ConditionalCheckFailedException"}}, "UpdateItem"
    )
    edge_presign_service.dynamo_service.update_item.side_effect = client_error

    # Expect CloudFrontEdgeException due to ClientError in DynamoDB
    with pytest.raises(CloudFrontEdgeException) as exc_info:
        edge_presign_service.attempt_presign_ingestion(
            "hashed_uri", "example-lloyd.com"
        )

    # Assert the CloudFrontEdgeException properties match the expected LambdaError values
    assert exc_info.value.status_code == 400
    assert exc_info.value.err_code == LambdaError.EdgeNoClient.value["err_code"]
    assert exc_info.value.message == LambdaError.EdgeNoClient.value["message"]


def test_create_s3_response(edge_presign_service, request_values):
    # Prepare request with an authorization header
    request = {
        "headers": {
            "authorization": [{"key": "Authorization", "value": "Bearer some-token"}],
            "host": [{"key": "Host", "value": "example.com"}],
        }
    }

    response = edge_presign_service.create_s3_response(request, request_values)
    assert "authorization" not in response["headers"]
    assert response["headers"]["host"][0]["value"] == "example-lloyd.com"


def test_filter_request_values_success(edge_presign_service):
    request = {
        "uri": "/test/uri",
        "querystring": "X-Amz-Algorithm=algo&X-Amz-Date=20241028T143157Z",
        "headers": {"host": [{"key": "Host", "value": "example.com"}]},
        "origin": {"s3": {"domainName": "mocked-domain.com"}},
    }
    result = edge_presign_service.filter_request_values(request)
    assert result["uri"] == "/test/uri"
    assert result["querystring"] == "X-Amz-Algorithm=algo&X-Amz-Date=20241028T143157Z"
    assert result["domain_name"] == "mocked-domain.com"


def test_filter_request_values_missing_component(edge_presign_service):
    # Test with missing origin component
    request = {
        "uri": "/test/uri",
        "querystring": "X-Amz-Algorithm=algo&X-Amz-Date=20241028T143157Z",
        "headers": {"host": [{"key": "Host", "value": "example.com"}]},
    }
    with pytest.raises(CloudFrontEdgeException) as exc_info:
        edge_presign_service.filter_request_values(request)

    # Assert the exception matches the LambdaError.EdgeNoOrigin dictionary
    assert exc_info.value.status_code == 500
    assert exc_info.value.err_code == LambdaError.EdgeNoOrigin.value["err_code"]
    assert exc_info.value.message == LambdaError.EdgeNoOrigin.value["message"]


def test_filter_domain_for_env(edge_presign_service):
    # Test different domain patterns
    assert edge_presign_service.filter_domain_for_env("example-lloyd.com") == "example"
    assert (
        edge_presign_service.filter_domain_for_env("sub-test-lloyd.com") == "sub-test"
    )
    assert edge_presign_service.filter_domain_for_env("invalid.com") == ""


def test_extend_table_name(edge_presign_service):
    # Test with and without environment
    assert (
        edge_presign_service.extend_table_name("base_table", "test")
        == "test_base_table"
    )
    assert edge_presign_service.extend_table_name("base_table", "") == "base_table"
