import json

import pytest
from enums.lambda_error import LambdaError
from handlers.virus_scan_result_handler import lambda_handler
from utils.lambda_exceptions import VirusScanResultException
from utils.lambda_response import ApiGatewayResponse

VALID_EVENT = {"documentReference": "FILE_REF_TEST"}


@pytest.fixture
def mock_virus_scan_service(mocker):
    mocked_class = mocker.patch(
        "handlers.virus_scan_result_handler.VirusScanResultService"
    )
    mocked_service = mocked_class.return_value
    yield mocked_service


def test_lambda_handler_respond_with_200(context, set_env, mock_virus_scan_service):
    valid_event = {"httpMethod": "POST", "body": json.dumps(VALID_EVENT)}
    expected = ApiGatewayResponse(
        200, "Virus Scan was successful", "POST"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_event, context)

    assert actual == expected

    mock_virus_scan_service.prepare_request.assert_called_once()


def test_lambda_handler_respond_with_400_when_file_unclean(
    context, set_env, mock_virus_scan_service
):
    valid_event = {"httpMethod": "POST", "body": json.dumps(VALID_EVENT)}

    mock_virus_scan_service.prepare_request.side_effect = VirusScanResultException(
        400, LambdaError.MockError
    )
    actual = lambda_handler(valid_event, context)

    expected = ApiGatewayResponse(
        400, json.dumps(LambdaError.MockError.value), "POST"
    ).create_api_gateway_response()

    assert actual == expected

    mock_virus_scan_service.prepare_request.assert_called_once()


def test_lambda_handler_respond_with_400_when_no_body(
    context, set_env, mock_virus_scan_service
):
    valid_event = {
        "httpMethod": "POST",
    }
    expected_body = json.dumps(
        {
            "message": "Missing event body",
            "err_code": "VSR_4001",
            "interaction_id": "88888888-4444-4444-4444-121212121212",
        }
    )
    actual = lambda_handler(valid_event, context)

    expected = ApiGatewayResponse(
        400, expected_body, "POST"
    ).create_api_gateway_response()

    assert actual == expected

    mock_virus_scan_service.prepare_request.assert_not_called()


def test_lambda_handler_respond_with_400_when_invalid_body(
    context, set_env, mock_virus_scan_service
):
    valid_event = {"httpMethod": "POST", "body": "invalid_body"}
    expected_body = json.dumps(
        {
            "message": "Missing event body",
            "err_code": "VSR_4001",
            "interaction_id": "88888888-4444-4444-4444-121212121212",
        }
    )
    actual = lambda_handler(valid_event, context)

    expected = ApiGatewayResponse(
        400, expected_body, "POST"
    ).create_api_gateway_response()

    assert actual == expected

    mock_virus_scan_service.prepare_request.assert_not_called()
