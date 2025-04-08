import copy
import json

import pytest
from enums.lambda_error import LambdaError
from handlers.edge_presign_handler import lambda_handler
from tests.unit.conftest import MOCKED_LG_BUCKET_URL
from tests.unit.enums.test_edge_presign_values import MOCK_S3_EDGE_EVENT
from utils.lambda_exceptions import CloudFrontEdgeException


@pytest.fixture
def valid_event():
    return MOCK_S3_EDGE_EVENT


@pytest.fixture
def mock_edge_presign_service(mocker):
    mock_edge_service = mocker.patch("handlers.edge_presign_handler.EdgePresignService")
    mock_edge_service_instance = mock_edge_service.return_value
    return mock_edge_service_instance


def test_lambda_handler_success(valid_event, context, mock_edge_presign_service):
    request_body = valid_event["Records"][0]["cf"]["request"]
    modified_request = copy.deepcopy(request_body)
    modified_request["uri"] = "/path/to/resource"
    modified_request["querystring"] = "key=value"
    mock_edge_presign_service.use_presign.return_value = modified_request
    mock_edge_presign_service.update_s3_headers.return_value = modified_request

    response = lambda_handler(valid_event, context)

    mock_edge_presign_service.use_presign.assert_called_once_with(request_body)
    mock_edge_presign_service.update_s3_headers.assert_called_once_with(
        modified_request
    )

    assert response["headers"]["host"][0]["value"] == MOCKED_LG_BUCKET_URL
    assert response["uri"] == "/path/to/resource"
    assert response["querystring"] == "key=value"


def test_lambda_handler_exception(valid_event, context, mock_edge_presign_service):
    mock_edge_presign_service.use_presign.side_effect = CloudFrontEdgeException(
        400, LambdaError.MockError
    )

    response = lambda_handler(valid_event, context)

    actual_status = response["status"]
    actual_response = json.loads(response["body"])

    assert actual_status == 400
    assert actual_response["message"] == "Client error"
    assert actual_response["err_code"] == "AB_XXXX"
