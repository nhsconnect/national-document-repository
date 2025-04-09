from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError
from services.edge_presign_service import EdgePresignService
from tests.unit.conftest import MOCK_TABLE_NAME, MOCKED_LG_BUCKET_URL
from tests.unit.enums.test_edge_presign_values import (
    EXPECTED_EDGE_NO_CLIENT_ERROR_CODE,
    EXPECTED_EDGE_NO_CLIENT_ERROR_MESSAGE,
    MOCKED_AUTH_QUERY,
)
from utils.lambda_exceptions import CloudFrontEdgeException


@pytest.fixture
@patch("services.edge_presign_service.SSMService")
@patch("services.edge_presign_service.DynamoDBService")
def edge_presign_service(mock_ssm_service, mock_dynamo_service):
    mock_ssm_service.get_ssm_parameter.return_value = MOCK_TABLE_NAME
    mock_dynamo_service.update_item.return_value = {
        "Attributes": {
            "presignedUrl": f"https://{MOCKED_LG_BUCKET_URL}/some/path?querystring"
        }
    }
    return EdgePresignService()


@pytest.fixture
def request_values():
    return {
        "uri": "/some/path",
        "querystring": MOCKED_AUTH_QUERY,
        "origin": {
            "s3": {
                "domainName": MOCKED_LG_BUCKET_URL,
            }
        },
        "headers": {
            "authorization": "some_auth",
        },
    }


def test_use_presign(edge_presign_service, request_values, mocker):
    mock_attempt_presign_ingestion = mocker.patch.object(
        edge_presign_service, "attempt_presign_ingestion"
    )
    mock_attempt_presign_ingestion.return_value = (
        "https://example.com/someother/path?querystring"
    )

    request_result = edge_presign_service.use_presign(request_values)

    mock_attempt_presign_ingestion.assert_called_once_with(
        "some/path", MOCKED_LG_BUCKET_URL
    )
    assert request_result.get("uri") == "/someother/path"
    assert request_result.get("querystring") == "querystring"


def test_attempt_presign_ingestion_success(edge_presign_service):
    try:
        edge_presign_service.dynamo_service.update_item.return_value = {
            "Attributes": {
                "presignedUrl": f"https://{MOCKED_LG_BUCKET_URL}/some/path?querystring"
            }
        }
        result = edge_presign_service.attempt_presign_ingestion(
            "random id", MOCKED_LG_BUCKET_URL
        )

        edge_presign_service.dynamo_service.update_item.assert_called_once()
        edge_presign_service.ssm_service.get_ssm_parameter.assert_called_once()
        assert result == f"https://{MOCKED_LG_BUCKET_URL}/some/path?querystring"
    except CloudFrontEdgeException:
        assert False


def test_attempt_presign_ingestion_client_error(edge_presign_service):
    client_error = ClientError(
        {"Error": {"Code": "ConditionalCheckFailedException"}}, "UpdateItem"
    )
    edge_presign_service.dynamo_service.update_item.side_effect = client_error

    with pytest.raises(CloudFrontEdgeException) as exc_info:
        edge_presign_service.attempt_presign_ingestion(
            "hashed_uri", MOCKED_LG_BUCKET_URL
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.err_code == EXPECTED_EDGE_NO_CLIENT_ERROR_CODE
    assert exc_info.value.message == EXPECTED_EDGE_NO_CLIENT_ERROR_MESSAGE


def test_update_s3_headers(edge_presign_service, request_values):
    response = edge_presign_service.update_s3_headers(request_values)
    assert "authorization" not in response["headers"]
    assert response["headers"]["host"][0]["value"] == MOCKED_LG_BUCKET_URL


@pytest.mark.parametrize(
    ["domain_name", "expected_environment"],
    [
        ("test-env-lloyd.example.com", "test-env"),
        ("ndra-lloyd-test-test.com", "ndra"),
        ("ndr-test-lloyd-test-test.com", "ndr-test"),
        ("pre-prod-lloyd-test-test.com", "pre-prod"),
        ("prod-lloyd-test-test.com", "prod"),
        ("lloyd-test-test.com", ""),
        ("invalid.com", ""),
    ],
)
def test_filter_domain_for_env(edge_presign_service, domain_name, expected_environment):
    domain_name = domain_name
    environment = edge_presign_service._filter_domain_for_env(domain_name)
    assert environment == expected_environment


@pytest.mark.parametrize("environment", ["test-env", "", "prod"])
def test_extend_table_name(edge_presign_service, environment):
    edge_presign_service.ssm_service.get_ssm_parameter.return_value = MOCK_TABLE_NAME
    table_name = edge_presign_service._get_formatted_table_name(environment)
    assert (
        table_name == f"{environment}_{MOCK_TABLE_NAME}"
        if environment
        else MOCK_TABLE_NAME
    )


def test_extract_presigned_url(edge_presign_service):
    updated_item = {
        "Attributes": {"presignedUrl": "https://example.com/test-id?key=value"}
    }
    presigned_url = edge_presign_service._extract_presigned_url(updated_item)
    assert presigned_url == "https://example.com/test-id?key=value"
