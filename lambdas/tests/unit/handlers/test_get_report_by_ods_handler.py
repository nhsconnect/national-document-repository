import json
import logging

import pytest
from handlers.get_report_by_ods_handler import (
    handle_api_gateway_request,
    handle_manual_trigger,
    lambda_handler,
)
from utils.exceptions import OdsErrorException
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = logging.getLogger()


@pytest.fixture
def mock_service(mocker):
    mock_service = mocker.Mock()
    mocker.patch(
        "handlers.get_report_by_ods_handler.OdsReportService", return_value=mock_service
    )
    return mock_service


@pytest.fixture
def mock_jwt_encode(mocker):
    decoded_token = {"selected_organisation": {"org_ods_code": "ODS123"}}
    yield mocker.patch("jwt.decode", return_value=decoded_token)


def test_lambda_handler_api_gateway_request(
    mock_service, set_env, context, mock_jwt_encode
):
    event = {"httpMethod": "GET", "headers": {"Authorization": "mock_token"}}
    mock_service.get_nhs_numbers_by_ods.return_value = "example.com/presigned-url"
    expected = ApiGatewayResponse(
        200, json.dumps({"url": "example.com/presigned-url"}), "GET"
    ).create_api_gateway_response()

    result = lambda_handler(event, context)
    assert result == expected

    mock_service.get_nhs_numbers_by_ods.assert_called_once_with(
        "ODS123", is_pre_signed_need=True
    )


def test_lambda_handler_manual_trigger(mock_service, set_env, context):
    event = {"odsCode": "ODS123,ODS456"}
    mock_service.get_nhs_numbers_by_ods.return_value = None
    expected = ApiGatewayResponse(
        200, "Successfully created report", "GET"
    ).create_api_gateway_response()

    result = lambda_handler(event, context)

    assert result == expected
    assert mock_service.get_nhs_numbers_by_ods.call_count == 2
    mock_service.get_nhs_numbers_by_ods.assert_any_call("ODS123")
    mock_service.get_nhs_numbers_by_ods.assert_any_call("ODS456")


def test_handle_api_gateway_request_no_ods_code(mock_service):
    event = {"httpMethod": "GET"}
    request_context.authorization = {"selected_organisation": {"org_ods_code": None}}

    with pytest.raises(OdsErrorException, match="No ODS code provided"):
        handle_api_gateway_request(event)


def test_handle_manual_trigger_single_ods_code(mock_service):
    event = {"odsCode": "ODS123"}
    mock_service.get_nhs_numbers_by_ods.return_value = None
    expected = ApiGatewayResponse(
        200, "Successfully created report", "GET"
    ).create_api_gateway_response()

    result = handle_manual_trigger(event)

    assert result == expected
    assert mock_service.get_nhs_numbers_by_ods.call_count == 1
    mock_service.get_nhs_numbers_by_ods.assert_called_once_with("ODS123")


def test_handle_manual_trigger_invalid_ods_code_format(mock_service):
    event = {"odsCode": "ODS123,ODS456,ODS789"}
    mock_service.get_nhs_numbers_by_ods.side_effect = OdsErrorException(
        "Invalid ODS code format"
    )

    with pytest.raises(OdsErrorException, match="Invalid ODS code format"):
        handle_manual_trigger(event)


def test_handle_api_gateway_request_service_error(mock_service):
    event = {"httpMethod": "GET"}
    request_context.authorization = {
        "selected_organisation": {"org_ods_code": "ODS123"}
    }
    mock_service.get_nhs_numbers_by_ods.side_effect = OdsErrorException(
        "Invalid ODS code format"
    )

    with pytest.raises(OdsErrorException, match="Invalid ODS code format"):
        handle_api_gateway_request(event)
