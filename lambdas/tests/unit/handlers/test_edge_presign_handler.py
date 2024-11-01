import copy
import json

import pytest
from handlers.edge_presign_handler import lambda_handler
from tests.unit.conftest import MOCK_TABLE_NAME, MOCKED_LG_BUCKET_URL
from tests.unit.enums.test_edge_presign_values import (
    EXPECTED_EDGE_MALFORMED_HEADER_ERROR_CODE,
    EXPECTED_EDGE_MALFORMED_HEADER_MESSAGE,
    EXPECTED_EDGE_MALFORMED_QUERY_ERROR_CODE,
    EXPECTED_EDGE_MALFORMED_QUERY_MESSAGE,
    EXPECTED_EDGE_NO_ORIGIN_ERROR_CODE,
    EXPECTED_EDGE_NO_ORIGIN_ERROR_MESSAGE,
    EXPECTED_EDGE_NO_QUERY_ERROR_CODE,
    EXPECTED_EDGE_NO_QUERY_MESSAGE,
    MOCK_S3_EDGE_EVENT,
    MOCKED_AUTH_QUERY,
    MOCKED_PARTIAL_QUERY,
)


@pytest.fixture
def valid_event():
    return copy.deepcopy(MOCK_S3_EDGE_EVENT)


@pytest.fixture
def mock_edge_presign_service(mocker):
    mock_ssm_service = mocker.patch("services.edge_presign_service.SSMService")
    mock_ssm_service_instance = mock_ssm_service.return_value
    mock_ssm_service_instance.get_ssm_parameter.return_value = MOCK_TABLE_NAME

    mock_dynamo_service = mocker.patch("services.edge_presign_service.DynamoDBService")
    mock_dynamo_service_instance = mock_dynamo_service.return_value
    mock_dynamo_service_instance.update_item.return_value = None

    mock_edge_service = mocker.patch("handlers.edge_presign_handler.EdgePresignService")
    mock_edge_service_instance = mock_edge_service.return_value
    mock_edge_service_instance.filter_request_values.return_value = {
        "uri": "/some/path",
        "querystring": MOCKED_AUTH_QUERY,
        "headers": {"host": [{"key": "Host", "value": MOCKED_LG_BUCKET_URL}]},
        "domain_name": MOCKED_LG_BUCKET_URL,
    }
    mock_edge_service_instance.use_presign.return_value = None
    mock_edge_service_instance.update_s3_headers.return_value = {
        "headers": {
            "host": [{"key": "Host", "value": MOCKED_LG_BUCKET_URL}],
        }
    }

    return mock_edge_service_instance


def test_lambda_handler_success(valid_event, context, mock_edge_presign_service):
    response = lambda_handler(valid_event, context)

    mock_edge_presign_service.filter_request_values.assert_called_once()
    mock_edge_presign_service.use_presign.assert_called_once_with(
        mock_edge_presign_service.filter_request_values.return_value
    )
    mock_edge_presign_service.update_s3_headers.assert_called_once_with(
        valid_event["Records"][0]["cf"]["request"],
        mock_edge_presign_service.filter_request_values.return_value,
    )

    assert response["headers"]["host"][0]["value"] == MOCKED_LG_BUCKET_URL


def test_lambda_handler_no_query_params(valid_event, context):
    event = copy.deepcopy(valid_event)
    event["Records"][0]["cf"]["request"]["querystring"] = ""

    response = lambda_handler(event, context)

    actual_status = response["status"]
    actual_response = json.loads(response["body"])

    assert actual_status == 500
    assert actual_response["message"] == EXPECTED_EDGE_NO_QUERY_MESSAGE
    assert actual_response["err_code"] == EXPECTED_EDGE_NO_QUERY_ERROR_CODE


def test_lambda_handler_missing_query_params(valid_event, context):
    event = copy.deepcopy(valid_event)
    event["Records"][0]["cf"]["request"]["querystring"] = MOCKED_PARTIAL_QUERY

    response = lambda_handler(event, context)

    actual_status = response["status"]
    actual_response = json.loads(response["body"])

    assert actual_status == 500
    assert actual_response["message"] == EXPECTED_EDGE_MALFORMED_QUERY_MESSAGE
    assert actual_response["err_code"] == EXPECTED_EDGE_MALFORMED_QUERY_ERROR_CODE


def test_lambda_handler_missing_headers(valid_event, context):
    event = copy.deepcopy(valid_event)
    event["Records"][0]["cf"]["request"]["headers"] = {}

    response = lambda_handler(event, context)

    actual_status = response["status"]
    actual_response = json.loads(response["body"])

    assert actual_status == 500
    assert actual_response["message"] == EXPECTED_EDGE_MALFORMED_HEADER_MESSAGE
    assert actual_response["err_code"] == EXPECTED_EDGE_MALFORMED_HEADER_ERROR_CODE


def test_lambda_handler_missing_origin(valid_event, context):
    event = copy.deepcopy(valid_event)
    event["Records"][0]["cf"]["request"]["origin"] = {}

    response = lambda_handler(event, context)

    actual_status = response["status"]
    actual_response = json.loads(response["body"])

    assert actual_status == 500
    assert actual_response["message"] == EXPECTED_EDGE_NO_ORIGIN_ERROR_MESSAGE
    assert actual_response["err_code"] == EXPECTED_EDGE_NO_ORIGIN_ERROR_CODE
