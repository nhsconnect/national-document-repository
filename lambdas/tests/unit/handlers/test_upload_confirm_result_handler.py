import json
from enum import Enum

import pytest
from handlers.upload_confirm_result_handler import (
    lambda_handler,
    processing_event_details,
)
from tests.unit.conftest import TEST_NHS_NUMBER
from tests.unit.helpers.data.upload_confirm_result import (
    MOCK_ARF_DOCUMENTS,
    MOCK_INVALID_BODY_EVENT,
    MOCK_INVALID_NHS_NUMBER_EVENT,
    MOCK_MISSING_BODY_EVENT,
    MOCK_MISSING_DOCUMENTS_EVENT,
    MOCK_MISSING_NHS_NUMBER_EVENT,
    MOCK_VALID_ARF_EVENT,
    MOCK_VALID_BOTH_DOC_TYPES_EVENT,
    MOCK_VALID_LG_EVENT,
)
from utils.lambda_exceptions import UploadConfirmResultException
from utils.lambda_response import ApiGatewayResponse


class MockError(Enum):
    Error = {
        "message": "Client error",
        "err_code": "AB_XXXX",
        "interaction_id": "88888888-4444-4444-4444-121212121212",
    }


@pytest.fixture
def mock_upload_confirm_result_service(mocker, mock_upload_lambda_enabled):
    mocked_class = mocker.patch(
        "handlers.upload_confirm_result_handler.UploadConfirmResultService"
    )
    mocker.patch.object(mocked_class, "process_documents")
    mocked_instance = mocked_class.return_value
    yield mocked_instance


@pytest.fixture
def mock_processing_event_details(mocker):
    yield mocker.patch(
        "handlers.upload_confirm_result_handler.processing_event_details",
        return_value=(TEST_NHS_NUMBER, MOCK_ARF_DOCUMENTS),
    )


def test_upload_confirm_result_handler_success_lg(
    set_env, context, mock_upload_confirm_result_service
):
    expected = ApiGatewayResponse(
        204, "Finished processing all documents", "POST"
    ).create_api_gateway_response()

    actual = lambda_handler(MOCK_VALID_LG_EVENT, context)

    assert expected == actual


def test_upload_confirm_result_handler_success_arf(
    set_env, context, mock_upload_confirm_result_service
):
    expected = ApiGatewayResponse(
        204, "Finished processing all documents", "POST"
    ).create_api_gateway_response()

    actual = lambda_handler(MOCK_VALID_ARF_EVENT, context)

    assert expected == actual


def test_upload_confirm_result_handler_success_both_doc_types(
    set_env, context, mock_upload_confirm_result_service
):
    expected = ApiGatewayResponse(
        204, "Finished processing all documents", "POST"
    ).create_api_gateway_response()

    actual = lambda_handler(MOCK_VALID_BOTH_DOC_TYPES_EVENT, context)

    assert expected == actual


arf_environment_variables = [
    "DOCUMENT_STORE_BUCKET_NAME",
    "DOCUMENT_STORE_DYNAMODB_NAME",
]
lg_environment_variables = ["LLOYD_GEORGE_BUCKET_NAME", "LLOYD_GEORGE_DYNAMODB_NAME"]


@pytest.mark.parametrize("environment_variable", lg_environment_variables)
def test_lambda_handler_missing_environment_variables_type_lg_returns_500(
    set_env,
    monkeypatch,
    environment_variable,
    context,
):
    monkeypatch.delenv(environment_variable)

    expected_body = {
        "message": f"An error occurred due to missing environment variable: '{environment_variable}'",
        "err_code": "ENV_5001",
        "interaction_id": "88888888-4444-4444-4444-121212121212",
    }
    expected = ApiGatewayResponse(
        500,
        json.dumps(expected_body),
        "POST",
    ).create_api_gateway_response()
    actual = lambda_handler(MOCK_VALID_LG_EVENT, context)
    assert expected == actual


@pytest.mark.parametrize("environment_variable", arf_environment_variables)
def test_lambda_handler_missing_environment_variables_type_arf_returns_500(
    set_env,
    monkeypatch,
    environment_variable,
    context,
):
    monkeypatch.delenv(environment_variable)

    expected_body = {
        "message": f"An error occurred due to missing environment variable: '{environment_variable}'",
        "err_code": "ENV_5001",
        "interaction_id": "88888888-4444-4444-4444-121212121212",
    }
    expected = ApiGatewayResponse(
        500,
        json.dumps(expected_body),
        "POST",
    ).create_api_gateway_response()
    actual = lambda_handler(MOCK_VALID_ARF_EVENT, context)
    assert expected == actual


def test_processing_event_details_event_with_invalid_body_raises_exception(
    set_env, context, mock_upload_confirm_result_service
):
    with pytest.raises(UploadConfirmResultException):
        processing_event_details(MOCK_INVALID_BODY_EVENT)


def test_processing_event_details_missing_body_raises_exception(
    set_env, context, mock_upload_confirm_result_service
):
    with pytest.raises(UploadConfirmResultException):
        processing_event_details(MOCK_MISSING_BODY_EVENT)


def test_processing_event_details_missing_nhs_number_raises_error():
    with pytest.raises(UploadConfirmResultException):
        processing_event_details(MOCK_MISSING_NHS_NUMBER_EVENT)


def test_processing_event_details_invalid_nhs_number_raises_error():
    with pytest.raises(UploadConfirmResultException):
        processing_event_details(MOCK_INVALID_NHS_NUMBER_EVENT)


def test_processing_event_details_missing_documents_raises_error():
    with pytest.raises(UploadConfirmResultException):
        processing_event_details(MOCK_MISSING_DOCUMENTS_EVENT)


def test_processing_event_details_returns_nhs_number_and_documents():
    try:
        expected_nhs_number = TEST_NHS_NUMBER
        expected_documents = MOCK_ARF_DOCUMENTS
        actual_nhs_number, actual_doc_list = processing_event_details(
            MOCK_VALID_ARF_EVENT
        )
        assert expected_nhs_number == actual_nhs_number
        assert expected_documents == actual_doc_list
    except UploadConfirmResultException:
        assert False, "test"


def test_lambda_handler_processing_event_details_raises_error(
    context, set_env, mock_processing_event_details, mock_upload_lambda_enabled
):
    mock_processing_event_details.side_effect = UploadConfirmResultException(
        400, MockError.Error
    )
    expected = ApiGatewayResponse(
        400,
        json.dumps(MockError.Error.value),
        "POST",
    ).create_api_gateway_response()
    actual = lambda_handler(MOCK_VALID_ARF_EVENT, context)
    assert expected == actual
    mock_processing_event_details.assert_called_with(MOCK_VALID_ARF_EVENT)


def test_lambda_handler_service_raises_error(
    context, set_env, mock_processing_event_details, mock_upload_confirm_result_service
):
    mock_processing_event_details.return_value = (TEST_NHS_NUMBER, MOCK_ARF_DOCUMENTS)
    mock_upload_confirm_result_service.process_documents.side_effect = (
        UploadConfirmResultException(400, MockError.Error)
    )
    expected = ApiGatewayResponse(
        400,
        json.dumps(MockError.Error.value),
        "POST",
    ).create_api_gateway_response()

    actual = lambda_handler(MOCK_VALID_ARF_EVENT, context)

    assert expected == actual
    mock_upload_confirm_result_service.process_documents.assert_called_with(
        MOCK_ARF_DOCUMENTS
    )
    mock_processing_event_details.assert_called_with(MOCK_VALID_ARF_EVENT)
