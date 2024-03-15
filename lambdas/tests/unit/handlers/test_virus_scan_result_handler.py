import json

import pytest
from enums.lambda_error import LambdaError
from handlers.virus_scan_result_handler import lambda_handler
from utils.lambda_exceptions import VirusScanResultException
from utils.lambda_response import ApiGatewayResponse

INVALID_DOCUMENT_REFERENCE = {"documentReference": "FILE_REF_TEST"}
VALID_DOCUMENT_REFERENCE = {"documentReference": "test/ARF/1111111111"}
VALID_DOCUMENT_REFERENCE_LOWERCASE = {"documentReference": "test/arf/1111111111"}


@pytest.fixture
def mock_virus_scan_service(mocker):
    mocked_class = mocker.patch("handlers.virus_scan_result_handler.VirusScanService")
    mocked_service = mocked_class.return_value
    yield mocked_service


def test_lambda_handler_respond_with_200(context, set_env, mock_virus_scan_service):
    valid_event = {"httpMethod": "POST", "body": json.dumps(VALID_DOCUMENT_REFERENCE)}
    expected = ApiGatewayResponse(
        200, "Virus Scan was successful", "POST"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_event, context)

    assert actual == expected

    mock_virus_scan_service.scan_file.assert_called_once()


def test_lambda_handler_responds_with_200_when_doctype_lowercase(
    context, set_env, mock_virus_scan_service
):
    valid_event = {
        "httpMethod": "POST",
        "body": json.dumps(VALID_DOCUMENT_REFERENCE_LOWERCASE),
    }
    expected = ApiGatewayResponse(
        200, "Virus Scan was successful", "POST"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_event, context)

    assert actual == expected
    mock_virus_scan_service.scan_file.assert_called_once()


def test_lambda_handler_respond_with_400_when_file_unclean(
    context, set_env, mock_virus_scan_service
):
    valid_event = {"httpMethod": "POST", "body": json.dumps(VALID_DOCUMENT_REFERENCE)}

    mock_virus_scan_service.scan_file.side_effect = VirusScanResultException(
        400, LambdaError.MockError
    )
    actual = lambda_handler(valid_event, context)

    expected = ApiGatewayResponse(
        400, json.dumps(LambdaError.MockError.value), "POST"
    ).create_api_gateway_response()

    assert actual == expected

    mock_virus_scan_service.scan_file.assert_called_once()


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

    mock_virus_scan_service.scan_file.assert_not_called()


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

    mock_virus_scan_service.scan_file.assert_not_called()


def test_lambda_handler_responds_with_400_when_no_doc_type_in_document_reference(
    context, set_env, mock_virus_scan_service
):
    no_doc_type_event = {
        "httpMethod": "POST",
        "body": json.dumps(INVALID_DOCUMENT_REFERENCE),
    }
    expected_body = json.dumps(
        {
            "message": "Document reference is missing a document type",
            "err_code": "VSR_4003",
            "interaction_id": "88888888-4444-4444-4444-121212121212",
        }
    )
    expected = ApiGatewayResponse(
        400, expected_body, "POST"
    ).create_api_gateway_response()

    actual = lambda_handler(no_doc_type_event, context)

    assert actual == expected
    mock_virus_scan_service.scan_file.assert_not_called()
