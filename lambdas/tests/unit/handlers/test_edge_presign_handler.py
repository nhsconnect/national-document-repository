import hashlib
from unittest.mock import Mock

import pytest
from handlers.edge_presign_handler import lambda_handler
from services.edge_presign_service import EdgePresignService

# Set the table name globally for all tests
TABLE_NAME = "CloudFrontEdgeReference"


# Utility function to create a mock context
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
                            "host": [{"key": "Host", "value": "example.com"}],
                        },
                        "querystring": "origin=https://test.example.com&other=param",
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
                            "host": [{"key": "Host", "value": "example.com"}],
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
    return mocker.patch.object(
        EdgePresignService, "attempt_url_update", return_value=None
    )


def test_lambda_handler_valid_event(valid_event, mocker, mock_edge_presign_service):
    # Use the mock context
    context = mock_context()

    uri = valid_event["Records"][0]["cf"]["request"]["uri"]
    querystring = valid_event["Records"][0]["cf"]["request"]["querystring"]
    expected_uri_hash = hashlib.md5(f"{uri}?{querystring}".encode("utf-8")).hexdigest()

    # Expected output (assuming EdgePresignService returns None)
    expected = {
        "uri": "/some/path",
        "querystring": "origin=https://test.example.com&other=param",
        "headers": {
            "host": [{"key": "Host", "value": "example.com"}],
        },
    }

    actual = lambda_handler(valid_event, context)
    assert actual == expected

    mock_edge_presign_service.assert_called_once_with(
        table_name=TABLE_NAME,
        uri_hash=expected_uri_hash,
        origin_url="https://test.example.com",
    )


def test_lambda_handler_missing_origin(
    missing_origin_event, mocker, mock_edge_presign_service
):
    # Use the mock context
    context = mock_context()

    uri = missing_origin_event["Records"][0]["cf"]["request"]["uri"]
    querystring = missing_origin_event["Records"][0]["cf"]["request"]["querystring"]
    expected_uri_hash = hashlib.md5(f"{uri}?{querystring}".encode("utf-8")).hexdigest()

    # Expected output (assuming no origin and EdgePresignService returns None)
    expected = {
        "uri": "/some/path",
        "querystring": "other=param",
        "headers": {
            "host": [{"key": "Host", "value": "example.com"}],
        },
    }

    actual = lambda_handler(missing_origin_event, context)
    assert actual == expected

    mock_edge_presign_service.assert_called_once_with(
        table_name=TABLE_NAME, uri_hash=expected_uri_hash, origin_url=""
    )


def test_lambda_handler_service_error(valid_event, mocker):
    context = mock_context()
    expected_response = {
        "status": "500",
        "statusDescription": "Internal Server Error",
        "headers": {
            "content-type": [{"key": "Content-Type", "value": "text/plain"}],
            "content-encoding": [{"key": "Content-Encoding", "value": "UTF-8"}],
        },
        "body": "Internal Server Error",
    }

    mocker.patch.object(
        EdgePresignService, "attempt_url_update", return_value=expected_response
    )

    actual = lambda_handler(valid_event, context)
    assert actual == expected_response
