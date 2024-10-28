import copy
import json
from unittest.mock import Mock

import pytest
from handlers.edge_presign_handler import lambda_handler
from tests.unit.enums.test_edge_presign_values import (
    EXPECTED_EDGE_MALFORMED_HEADER_ERROR_CODE,
    EXPECTED_EDGE_MALFORMED_HEADER_MESSAGE,
    EXPECTED_EDGE_MALFORMED_QUERY_ERROR_CODE,
    EXPECTED_EDGE_MALFORMED_QUERY_MESSAGE,
    EXPECTED_EDGE_NO_ORIGIN_ERROR_CODE,
    EXPECTED_EDGE_NO_ORIGIN_ERROR_MESSAGE,
    EXPECTED_EDGE_NO_QUERY_ERROR_CODE,
    EXPECTED_EDGE_NO_QUERY_MESSAGE,
    MOCKED_AUTH_QUERY,
    MOCKED_DOMAIN,
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

    mock_edge_service = mocker.patch("handlers.edge_presign_handler.EdgePresignService")
    mock_edge_service_instance = mock_edge_service.return_value
    mock_edge_service_instance.extract_request_values.return_value = {
        "uri": "/some/path",
        "querystring": MOCKED_AUTH_QUERY,
        "headers": {"host": [{"key": "Host", "value": MOCKED_DOMAIN}]},
        "domain_name": MOCKED_DOMAIN,
    }
    mock_edge_service_instance.presign_request.return_value = None
    mock_edge_service_instance.prepare_s3_response.return_value = {
        "headers": {
            "host": [{"key": "Host", "value": MOCKED_DOMAIN}],
        }
    }

    return mock_edge_service_instance


def test_lambda_handler_success(valid_event, mock_edge_presign_service):
    context = mock_context()
    response = lambda_handler(valid_event, context)

    mock_edge_presign_service.extract_request_values.assert_called_once()
    mock_edge_presign_service.presign_request.assert_called_once_with(
        mock_edge_presign_service.extract_request_values.return_value
    )
    mock_edge_presign_service.prepare_s3_response.assert_called_once_with(
        valid_event["Records"][0]["cf"]["request"],
        mock_edge_presign_service.extract_request_values.return_value,
    )

    assert response["headers"]["host"][0]["value"] == MOCKED_DOMAIN


def test_lambda_handler_no_query_params(valid_event, mock_edge_presign_service):
    context = mock_context()
    event = copy.deepcopy(valid_event)
    event["Records"][0]["cf"]["request"]["querystring"] = ""

    response = lambda_handler(event, context)

    actual_status = response["status"]
    actual_response = json.loads(response["body"])

    assert actual_status == 500
    assert actual_response["message"] == EXPECTED_EDGE_NO_QUERY_MESSAGE
    assert actual_response["err_code"] == EXPECTED_EDGE_NO_QUERY_ERROR_CODE


def test_lambda_handler_missing_query_params(valid_event, mock_edge_presign_service):
    context = mock_context()
    event = copy.deepcopy(valid_event)
    event["Records"][0]["cf"]["request"]["querystring"] = (
        "X-Amz-Algorithm=algo&X-Amz-Credential=cred&X-Amz-Date=date"
        "&X-Amz-Expires=3600"
    )

    response = lambda_handler(event, context)

    actual_status = response["status"]
    actual_response = json.loads(response["body"])

    assert actual_status == 500
    assert actual_response["message"] == EXPECTED_EDGE_MALFORMED_QUERY_MESSAGE
    assert actual_response["err_code"] == EXPECTED_EDGE_MALFORMED_QUERY_ERROR_CODE


def test_lambda_handler_missing_headers(valid_event, mock_edge_presign_service):
    context = mock_context()
    event = copy.deepcopy(valid_event)
    event["Records"][0]["cf"]["request"]["headers"] = {}

    response = lambda_handler(event, context)

    actual_status = response["status"]
    actual_response = json.loads(response["body"])

    assert actual_status == 500
    assert actual_response["message"] == EXPECTED_EDGE_MALFORMED_HEADER_MESSAGE
    assert actual_response["err_code"] == EXPECTED_EDGE_MALFORMED_HEADER_ERROR_CODE


def test_lambda_handler_missing_origin(valid_event, mock_edge_presign_service):
    context = mock_context()
    event = copy.deepcopy(valid_event)
    event["Records"][0]["cf"]["request"]["origin"] = {}

    response = lambda_handler(event, context)

    actual_status = response["status"]
    actual_response = json.loads(response["body"])

    assert actual_status == 500
    assert actual_response["message"] == EXPECTED_EDGE_NO_ORIGIN_ERROR_MESSAGE
    assert actual_response["err_code"] == EXPECTED_EDGE_NO_ORIGIN_ERROR_CODE
