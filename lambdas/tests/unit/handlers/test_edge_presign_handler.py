import copy
import json
from unittest.mock import Mock

import pytest
from handlers.edge_presign_handler import lambda_handler
from tests.unit.enums.test_edge_presign_values import (
    EXPECTED_DOMAIN,
    EXPECTED_EDGE_MALFORMED_ERROR_CODE,
    EXPECTED_EDGE_MALFORMED_ERROR_MESSAGE,
    EXPECTED_EDGE_MALFORMED_HEADER_ERROR_CODE,
    EXPECTED_EDGE_MALFORMED_HEADER_ERROR_MESSAGE,
    EXPECTED_EDGE_MALFORMED_QUERY_ERROR_CODE,
    EXPECTED_EDGE_MALFORMED_QUERY_ERROR_MESSAGE,
    EXPECTED_EDGE_NO_ORIGIN_ERROR_CODE,
    EXPECTED_EDGE_NO_ORIGIN_ERROR_MESSAGE,
    TABLE_NAME,
    VALID_EVENT_MODEL,
)


def mock_context():
    context = Mock()
    context.aws_request_id = "fake_request_id"
    return context


@pytest.fixture
def valid_event():
    return copy.deepcopy(VALID_EVENT_MODEL)


@pytest.fixture
def mock_edge_presign_service(mocker):
    mock_ssm_service = mocker.patch("services.edge_presign_service.SSMService")
    mock_ssm_service_instance = mock_ssm_service.return_value
    mock_ssm_service_instance.get_ssm_parameter.return_value = TABLE_NAME

    mock_dynamo_service = mocker.patch("services.edge_presign_service.DynamoDBService")
    mock_dynamo_service_instance = mock_dynamo_service.return_value
    mock_dynamo_service_instance.update_item.return_value = None

    return mock_ssm_service_instance, mock_dynamo_service_instance


def test_lambda_handler_success(valid_event, mock_edge_presign_service):
    context = mock_context()

    valid_event["Records"][0]["cf"]["request"]["headers"][
        "cloudfront-viewer-country"
    ] = [{"key": "CloudFront-Viewer-Country", "value": "US"}]
    valid_event["Records"][0]["cf"]["request"]["headers"]["x-forwarded-for"] = [
        {"key": "X-Forwarded-For", "value": "1.2.3.4"}
    ]

    valid_event["Records"][0]["cf"]["request"]["querystring"] = (
        "X-Amz-Algorithm=algo&X-Amz-Credential=cred&X-Amz-Date=date"
        "&X-Amz-Expires=3600&X-Amz-SignedHeaders=signed"
        "&X-Amz-Signature=sig&X-Amz-Security-Token=token"
    )
    response = lambda_handler(valid_event, context)

    assert "authorization" not in response["headers"]
    assert response["headers"]["host"][0]["value"] == EXPECTED_DOMAIN


def test_lambda_handler_missing_query_params(valid_event, mock_edge_presign_service):
    context = mock_context()
    event = copy.deepcopy(valid_event)
    event["Records"][0]["cf"]["request"]["querystring"] = ""
    response = lambda_handler(event, context)

    actual_status = response["status"]
    actual_response = json.loads(response["body"])

    assert actual_status == 500
    assert actual_response["message"] == EXPECTED_EDGE_MALFORMED_QUERY_ERROR_MESSAGE
    assert actual_response["err_code"] == EXPECTED_EDGE_MALFORMED_QUERY_ERROR_CODE


def test_lambda_handler_missing_headers(valid_event, mock_edge_presign_service):
    context = mock_context()
    event = copy.deepcopy(valid_event)
    event["Records"][0]["cf"]["request"]["headers"] = {}
    event["Records"][0]["cf"]["request"]["querystring"] = (
        "X-Amz-Algorithm=algo&X-Amz-Credential=cred&X-Amz-Date=date"
        "&X-Amz-Expires=3600&X-Amz-SignedHeaders=signed"
        "&X-Amz-Signature=sig&X-Amz-Security-Token=token"
    )
    response = lambda_handler(event, context)

    actual_status = response["status"]
    actual_response = json.loads(response["body"])

    assert actual_status == 500
    assert actual_response["message"] == EXPECTED_EDGE_MALFORMED_HEADER_ERROR_MESSAGE
    assert actual_response["err_code"] == EXPECTED_EDGE_MALFORMED_HEADER_ERROR_CODE


def test_lambda_handler_missing_origin(valid_event, mock_edge_presign_service):
    context = mock_context()
    event = copy.deepcopy(valid_event)
    event["Records"][0]["cf"]["request"]["origin"] = {}
    event["Records"][0]["cf"]["request"]["querystring"] = (
        "X-Amz-Algorithm=algo&X-Amz-Credential=cred&X-Amz-Date=date"
        "&X-Amz-Expires=3600&X-Amz-SignedHeaders=signed"
        "&X-Amz-Signature=sig&X-Amz-Security-Token=token"
    )
    response = lambda_handler(event, context)

    actual_status = response["status"]
    actual_response = json.loads(response["body"])

    assert actual_status == 500
    assert actual_response["message"] == EXPECTED_EDGE_NO_ORIGIN_ERROR_MESSAGE
    assert actual_response["err_code"] == EXPECTED_EDGE_NO_ORIGIN_ERROR_CODE


def test_lambda_handler_generic_edge_malformed(valid_event, mock_edge_presign_service):
    context = mock_context()
    event = copy.deepcopy(valid_event)
    event["Records"][0]["cf"]["request"].pop("uri", None)

    response = lambda_handler(event, context)
    actual_status = response["status"]
    actual_response = json.loads(response["body"])

    assert actual_status == 500
    assert actual_response["message"] == EXPECTED_EDGE_MALFORMED_ERROR_MESSAGE
    assert actual_response["err_code"] == EXPECTED_EDGE_MALFORMED_ERROR_CODE
