import pytest
from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from services.edge_presign_service import EdgePresignService
from utils.lambda_exceptions import CloudFrontEdgeException

# Instantiate the service for testing
edge_presign_service = EdgePresignService()

# Global Variables
TABLE_NAME = "CloudFrontEdgeReference"
NHS_DOMAIN = "example.gov.uk"


@pytest.fixture
def mock_dynamo_service(mocker):
    return mocker.patch.object(edge_presign_service, "dynamo_service", autospec=True)


@pytest.fixture
def mock_ssm_service(mocker):
    return mocker.patch.object(edge_presign_service, "ssm_service", autospec=True)


@pytest.fixture
def valid_origin_url():
    return f"https://test.{NHS_DOMAIN}"


@pytest.fixture
def invalid_origin_url():
    return f"https://invalid.{NHS_DOMAIN}"


def test_attempt_url_update_success(
    mock_dynamo_service, mock_ssm_service, valid_origin_url
):
    # Setup
    mock_dynamo_service.update_conditional.return_value = None
    mock_ssm_service.get_ssm_parameter.return_value = TABLE_NAME
    uri_hash = "valid_hash"

    # Action
    response = edge_presign_service.attempt_url_update(
        uri_hash=uri_hash, origin_url=valid_origin_url
    )

    # Assert
    assert response is None  # Success scenario returns None
    mock_ssm_service.get_ssm_parameter.assert_called_once_with("EDGE_REFERENCE_TABLE")
    mock_dynamo_service.update_conditional.assert_called_once_with(
        table_name="test_" + TABLE_NAME,
        key=uri_hash,
        updated_fields={"IsRequested": True},
        condition_expression="attribute_not_exists(IsRequested) OR IsRequested = :false",
        expression_attribute_values={":false": False},
    )


def test_attempt_url_update_client_error(
    mock_dynamo_service, mock_ssm_service, valid_origin_url
):
    # Setup
    mock_dynamo_service.update_conditional.side_effect = ClientError(
        {"Error": {"Code": "ConditionalCheckFailedException"}}, "UpdateItem"
    )
    mock_ssm_service.get_ssm_parameter.return_value = TABLE_NAME
    uri_hash = "valid_hash"

    # Assert that CloudFrontEdgeException is raised
    with pytest.raises(CloudFrontEdgeException) as exc_info:
        edge_presign_service.attempt_url_update(
            uri_hash=uri_hash, origin_url=valid_origin_url
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.message == LambdaError.EdgeNoClient.value["message"]


def test_extract_environment_from_url():
    # Test with valid NHS domain URL
    url = f"https://test.{NHS_DOMAIN}/path/to/resource"
    expected = "test"
    actual = edge_presign_service.extract_environment_from_url(url)
    assert actual == expected

    # Test with invalid URL (missing the environment part)
    url = f"https://{NHS_DOMAIN}/path/to/resource"
    expected = ""
    actual = edge_presign_service.extract_environment_from_url(url)
    assert actual == expected


def test_extend_table_name():
    # Test with valid environment
    base_table_name = TABLE_NAME
    environment = "test"
    expected = "test_" + base_table_name
    actual = edge_presign_service.extend_table_name(base_table_name, environment)
    assert actual == expected

    # Test with no environment
    environment = ""
    expected = base_table_name
    actual = edge_presign_service.extend_table_name(base_table_name, environment)
    assert actual == expected
