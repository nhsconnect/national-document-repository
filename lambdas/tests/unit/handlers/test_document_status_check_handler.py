import json

import pytest
from enums.lambda_error import LambdaError
from handlers.document_status_check_handler import lambda_handler
from tests.unit.conftest import MOCK_INTERACTION_ID, TEST_NHS_NUMBER
from utils.lambda_exceptions import UploadConfirmResultException
from utils.lambda_response import ApiGatewayResponse

MOCK_VALID_EVENT = {
    "queryStringParameters": {
        "patientId": TEST_NHS_NUMBER,
        "docIds": "doc-id-1,doc-id-2",
    },
}

MOCK_MISSING_PATIENT_ID_EVENT = {
    "queryStringParameters": {"docIds": "doc-id-1,doc-id-2"},
}

MOCK_MISSING_DOC_IDS_EVENT = {
    "queryStringParameters": {"patientId": TEST_NHS_NUMBER},
}

MOCK_EMPTY_DOC_IDS_EVENT = {
    "queryStringParameters": {"patientId": TEST_NHS_NUMBER, "docIds": ""},
}


@pytest.fixture
def mock_get_document_upload_status_service(mocker, mock_upload_lambda_enabled):
    mock_service_obj = mocker.MagicMock()
    mocked_class = mocker.patch(
        "handlers.document_status_check_handler.GetDocumentUploadStatusService",
        return_value=mock_service_obj,
    )
    mocker.patch.object(
        mock_service_obj,
        "get_document_references_by_id",
        return_value={"test-doc-id": {"status": "SUCCESS"}},
    )
    mocked_instance = mocked_class.return_value
    yield mocked_instance


def test_document_status_check_handler_success(
    set_env, context, mock_get_document_upload_status_service
):
    expected_body = json.dumps({"test-doc-id": {"status": "SUCCESS"}})
    expected = ApiGatewayResponse(
        200, expected_body, "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(MOCK_VALID_EVENT, context)

    assert expected == actual

    mock_get_document_upload_status_service.get_document_references_by_id.assert_called_with(
        document_ids=["doc-id-1", "doc-id-2"], nhs_number=TEST_NHS_NUMBER
    )


def test_document_status_check_handler_empty_result(
    set_env, context, mock_get_document_upload_status_service
):
    mock_get_document_upload_status_service.get_document_references_by_id.return_value = (
        []
    )

    expected = ApiGatewayResponse(404, json.dumps([]), methods="GET")

    actual = lambda_handler(MOCK_VALID_EVENT, context)

    assert expected == actual
    mock_get_document_upload_status_service.get_document_references_by_id.assert_called_with(
        document_ids=["doc-id-1", "doc-id-2"], nhs_number=TEST_NHS_NUMBER
    )


def test_lambda_handler_missing_patient_id(
    context, set_env, mock_upload_lambda_enabled
):
    expected_body = {
        "message": "An error occurred due to missing key",
        "err_code": "PN_4002",
        "interaction_id": MOCK_INTERACTION_ID,
    }
    expected = ApiGatewayResponse(
        400,
        json.dumps(expected_body),
        "GET",
    ).create_api_gateway_response()

    actual = lambda_handler(MOCK_MISSING_PATIENT_ID_EVENT, context)

    assert expected == actual


def test_lambda_handler_missing_doc_ids(context, set_env, mock_upload_lambda_enabled):
    expected_body = {
        "message": "Missing GET request query parameters",
        "err_code": "UC_4001",
        "interaction_id": MOCK_INTERACTION_ID,
    }
    expected = ApiGatewayResponse(
        400,
        json.dumps(expected_body),
        "GET",
    ).create_api_gateway_response()

    actual = lambda_handler(MOCK_MISSING_DOC_IDS_EVENT, context)

    assert expected == actual


def test_lambda_handler_empty_doc_ids(context, set_env, mock_upload_lambda_enabled):
    expected_body = {
        "message": "Missing GET request query parameters",
        "err_code": "UC_4001",
        "interaction_id": MOCK_INTERACTION_ID,
    }
    expected = ApiGatewayResponse(
        400,
        json.dumps(expected_body),
        "GET",
    ).create_api_gateway_response()

    actual = lambda_handler(MOCK_EMPTY_DOC_IDS_EVENT, context)

    assert expected == actual


def test_lambda_handler_service_raises_error(
    context,
    set_env,
    mock_get_document_upload_status_service,
    mock_upload_lambda_enabled,
):
    mock_get_document_upload_status_service.get_document_references_by_id.side_effect = UploadConfirmResultException(
        400, LambdaError.MockError
    )

    actual = lambda_handler(MOCK_VALID_EVENT, context)

    expected = ApiGatewayResponse(
        400,
        LambdaError.MockError.create_error_body(),
        "GET",
    ).create_api_gateway_response()
    assert expected == actual
    mock_get_document_upload_status_service.get_document_references_by_id.assert_called_with(
        document_ids=["doc-id-1", "doc-id-2"], nhs_number=TEST_NHS_NUMBER
    )


def test_no_event_processing_when_upload_lambda_flag_not_enabled(
    set_env, context, mock_upload_lambda_disabled
):
    expected_body = json.dumps(
        {
            "message": "Feature is not enabled",
            "err_code": "FFL_5003",
            "interaction_id": MOCK_INTERACTION_ID,
        }
    )
    expected = ApiGatewayResponse(
        500, expected_body, "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(MOCK_VALID_EVENT, context)

    assert actual == expected
