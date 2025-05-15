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
    mock_service.create_and_save_ods_report_based_on_ods.return_value = (
        "example.com/presigned-url"
    )
    expected = ApiGatewayResponse(
        200, json.dumps({"url": "example.com/presigned-url"}), "GET"
    ).create_api_gateway_response()

    result = lambda_handler(event, context)
    assert result == expected

    mock_service.create_and_save_ods_report_based_on_ods.assert_called_once_with(
        ods_code="ODS123",
        is_pre_signed_needed=True,
        is_upload_to_s3_needed=True,
        file_type_output="csv",
    )


def test_lambda_handler_manual_trigger(mock_service, set_env, context):
    event = {"odsCode": "ODS123,ODS456"}
    mock_service.create_and_save_ods_report_based_on_ods.return_value = None
    expected = ApiGatewayResponse(
        200, "Successfully created report", "GET"
    ).create_api_gateway_response()

    result = lambda_handler(event, context)

    assert result == expected
    assert mock_service.create_and_save_ods_report_based_on_ods.call_count == 2
    mock_service.create_and_save_ods_report_based_on_ods.assert_any_call(
        ods_code="ODS123", file_type_output="csv", is_upload_to_s3_needed=True
    )
    mock_service.create_and_save_ods_report_based_on_ods.assert_any_call(
        ods_code="ODS456", file_type_output="csv", is_upload_to_s3_needed=True
    )


@pytest.mark.parametrize(
    ["event", "output"],
    [
        ({"httpMethod": "GET"}, "csv"),
        ({"httpMethod": "GET", "queryStringParameters": None}, "csv"),
        (
            {"httpMethod": "GET", "queryStringParameters": {"outputFileFormat": "csv"}},
            "csv",
        ),
        (
            {"httpMethod": "GET", "queryStringParameters": {"outputFileFormat": "pdf"}},
            "pdf",
        ),
        (
            {
                "httpMethod": "GET",
                "queryStringParameters": {"outputFileFormat": "xlsx"},
            },
            "xlsx",
        ),
    ],
)
def test_handle_api_gateway_request_handles_no_query_string_params(
    mock_service, event, output
):
    request_context.authorization = {
        "selected_organisation": {"org_ods_code": "ODS123"}
    }
    mock_service.create_and_save_ods_report_based_on_ods.return_value = (
        "example.com/presigned-url"
    )

    handle_api_gateway_request(event)

    mock_service.create_and_save_ods_report_based_on_ods.assert_called_once_with(
        ods_code="ODS123",
        is_pre_signed_needed=True,
        is_upload_to_s3_needed=True,
        file_type_output=output,
    )


def test_handle_api_gateway_request_no_ods_code_raises_exception(mock_service):
    event = {"httpMethod": "GET"}
    request_context.authorization = {"selected_organisation": {"org_ods_code": None}}

    with pytest.raises(OdsErrorException, match="No ODS code provided"):
        handle_api_gateway_request(event)


def test_handle_api_gateway_request_invalid_ods_code_raises_exception(mock_service):
    event = {"httpMethod": "GET"}
    request_context.authorization = {
        "selected_organisation": {"org_ods_code": "ODS123"}
    }
    mock_service.create_and_save_ods_report_based_on_ods.side_effect = (
        OdsErrorException("Invalid ODS code format")
    )

    with pytest.raises(OdsErrorException, match="Invalid ODS code format"):
        handle_api_gateway_request(event)


def test_handle_manual_trigger_single_ods_code(mock_service):
    event = {"odsCode": "ODS123", "outputFileFormat": "pdf"}
    mock_service.create_and_save_ods_report_based_on_ods.return_value = None
    expected = ApiGatewayResponse(
        200, "Successfully created report", "GET"
    ).create_api_gateway_response()

    result = handle_manual_trigger(event)

    assert result == expected
    assert mock_service.create_and_save_ods_report_based_on_ods.call_count == 1
    mock_service.create_and_save_ods_report_based_on_ods.assert_called_once_with(
        ods_code="ODS123", file_type_output="pdf", is_upload_to_s3_needed=True
    )


def test_handle_manual_trigger_invalid_ods_code_format(mock_service):
    event = {"odsCode": "ODS123,ODS456,ODS789"}
    mock_service.create_and_save_ods_report_based_on_ods.side_effect = (
        OdsErrorException("Invalid ODS code format")
    )

    with pytest.raises(OdsErrorException, match="Invalid ODS code format"):
        handle_manual_trigger(event)
