import json

import pytest
from enums.lambda_error import LambdaError
from handlers.virus_scan_result_handler import lambda_handler
from tests.unit.conftest import TEST_NHS_NUMBER
from utils.lambda_exceptions import VirusScanResultException
from utils.lambda_response import ApiGatewayResponse

INVALID_DOCUMENT_REFERENCE = {"documentReference": "FILE_REF_TEST"}
VALID_DOCUMENT_REFERENCE = {
    "documentReference": f"test/ARF/{TEST_NHS_NUMBER}/1111111111"
}
VALID_DOCUMENT_REFERENCE_LOWERCASE = {
    "documentReference": f"test/arf/{TEST_NHS_NUMBER}/1111111111"
}


@pytest.fixture
def mock_virus_scan_service(
    mocker,
    mock_upload_lambda_enabled,
):
    mocked_class = mocker.patch("handlers.virus_scan_result_handler.VirusScanService")
    mocked_service = mocked_class.return_value
    yield mocked_service


def test_lambda_handler_respond_with_200(context, set_env, mock_virus_scan_service):
    valid_event = {
        "httpMethod": "POST",
        "body": json.dumps(VALID_DOCUMENT_REFERENCE),
        "queryStringParameters": {"patientId": TEST_NHS_NUMBER},
    }
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
        "queryStringParameters": {"patientId": TEST_NHS_NUMBER},
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
    valid_event = {
        "httpMethod": "POST",
        "body": json.dumps(VALID_DOCUMENT_REFERENCE),
        "queryStringParameters": {"patientId": TEST_NHS_NUMBER},
    }

    mock_virus_scan_service.scan_file.side_effect = VirusScanResultException(
        400, LambdaError.MockError
    )
    actual = lambda_handler(valid_event, context)

    expected = ApiGatewayResponse(
        400, LambdaError.MockError.create_error_body(), "POST"
    ).create_api_gateway_response()

    assert actual == expected

    mock_virus_scan_service.scan_file.assert_called_once()


def test_lambda_handler_respond_with_400_when_no_body(
    context, set_env, mock_virus_scan_service
):
    valid_event = {
        "httpMethod": "POST",
        "queryStringParameters": {"patientId": TEST_NHS_NUMBER},
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
    valid_event = {
        "httpMethod": "POST",
        "body": "invalid_body",
        "queryStringParameters": {"patientId": TEST_NHS_NUMBER},
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


def test_lambda_handler_responds_with_400_when_no_doc_type_in_document_reference(
    context, set_env, mock_virus_scan_service
):
    no_doc_type_event = {
        "httpMethod": "POST",
        "body": json.dumps(INVALID_DOCUMENT_REFERENCE),
        "queryStringParameters": {"patientId": TEST_NHS_NUMBER},
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


def test_lambda_handler_responds_with_400_when_nhs_number_does_not_match_in_document_reference(
    context, set_env, mock_virus_scan_service
):
    no_doc_type_event = {
        "httpMethod": "POST",
        "body": json.dumps(VALID_DOCUMENT_REFERENCE),
        "queryStringParameters": {"patientId": "1234567890"},
    }
    expected_body = json.dumps(
        {
            "message": "An error occurred due to patient number mismatch",
            "err_code": "PN_4003",
            "interaction_id": "88888888-4444-4444-4444-121212121212",
        }
    )
    expected = ApiGatewayResponse(
        400, expected_body, "POST"
    ).create_api_gateway_response()

    actual = lambda_handler(no_doc_type_event, context)

    assert actual == expected
    mock_virus_scan_service.scan_file.assert_not_called()


def test_no_event_processing_when_upload_lambda_flag_not_enabled(
    set_env, context, mock_upload_lambda_disabled
):

    valid_event = {
        "httpMethod": "POST",
        "body": json.dumps(VALID_DOCUMENT_REFERENCE_LOWERCASE),
        "queryStringParameters": {"patientId": TEST_NHS_NUMBER},
    }
    expected_body = json.dumps(
        {
            "message": "Feature is not enabled",
            "err_code": "FFL_5003",
            "interaction_id": "88888888-4444-4444-4444-121212121212",
        }
    )
    expected = ApiGatewayResponse(
        500, expected_body, "POST"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_event, context)

    assert actual == expected
