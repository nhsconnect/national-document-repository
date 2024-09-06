from unittest.mock import Mock

import pytest
from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from services.edge_presign_service import EdgePresignService
from utils.lambda_exceptions import CloudFrontEdgeException


def mock_context():
    context = Mock()
    context.aws_request_id = "fake_request_id"
    return context


@pytest.fixture
def valid_event():
    return {
        "Records": [
            {
                "cf": {
                    "request": {
                        "headers": {
                            "authorization": [
                                {"key": "Authorization", "value": "Bearer token"}
                            ],
                            "host": [{"key": "Host", "value": "example.gov.uk"}],
                        },
                        "querystring": "origin=https://test.example.gov.uk&other=param",
                        "uri": "/some/path",
                    }
                }
            }
        ]
    }


@pytest.fixture
def missing_origin_event():
    return {
        "Records": [
            {
                "cf": {
                    "request": {
                        "headers": {
                            "authorization": [
                                {"key": "Authorization", "value": "Bearer token"}
                            ],
                            "host": [{"key": "Host", "value": "example.gov.uk"}],
                        },
                        "querystring": "other=param",
                        "uri": "/some/path",
                    }
                }
            }
        ]
    }


@pytest.fixture
def mock_edge_presign_service(mocker):
    mock_ssm_service = mocker.patch("services.edge_presign_service.SSMService")
    mock_ssm_service_instance = mock_ssm_service.return_value
    mock_ssm_service_instance.get_ssm_parameter.return_value = "CloudFrontEdgeReference"

    mock_dynamo_service = mocker.patch("services.edge_presign_service.DynamoDBService")
    mock_dynamo_service_instance = mock_dynamo_service.return_value
    mock_dynamo_service_instance.update_conditional.return_value = None

    return mock_ssm_service_instance, mock_dynamo_service_instance


def test_attempt_url_update_success(mock_edge_presign_service):
    edge_service = EdgePresignService()
    env = "test"
    uri_hash = "test_uri_hash"
    origin_url = f"https://{env}.example.gov.uk"
    edge_service.ssm_service.get_ssm_parameter.return_value = "CloudFrontEdgeReference"

    edge_service.attempt_url_update(uri_hash, origin_url)
    edge_service.ssm_service.get_ssm_parameter.assert_called_once_with(
        "EDGE_REFERENCE_TABLE"
    )

    edge_service.dynamo_service.update_conditional.assert_called_once_with(
        table_name=f"{env}_CloudFrontEdgeReference",
        key=uri_hash,
        updated_fields={"IsRequested": True},
        condition_expression="attribute_not_exists(IsRequested) OR IsRequested = :false",
        expression_attribute_values={":false": False},
    )


def test_attempt_url_update_client_error(mock_edge_presign_service):
    edge_service = EdgePresignService()
    edge_service.dynamo_service.update_conditional.side_effect = ClientError(
        error_response={"Error": {"Code": "ConditionalCheckFailedException"}},
        operation_name="UpdateItem",
    )

    with pytest.raises(CloudFrontEdgeException) as exc_info:
        edge_service.attempt_url_update("test_uri_hash", "https://test.example.gov.uk")

    assert exc_info.value.status_code == 400
    assert exc_info.value.message == LambdaError.EdgeNoClient.value["message"]


def test_attempt_url_update_invalid_origin(mock_edge_presign_service):
    edge_service = EdgePresignService()
    result = edge_service.extract_environment_from_url("invalid_url")
    assert result == ""
