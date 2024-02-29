import json
from enum import Enum

import pytest
from handlers.create_document_reference_handler import (
    lambda_handler,
    processing_event_details,
)
from tests.unit.conftest import (
    MOCK_LG_STAGING_STORE_BUCKET,
    TEST_NHS_NUMBER,
    TEST_OBJECT_KEY,
)
from tests.unit.helpers.data.create_document_reference import (
    ARF_FILE_LIST,
    ARF_MOCK_EVENT_BODY,
    ARF_MOCK_RESPONSE,
    LG_AND_ARF_MOCK_RESPONSE,
    LG_MOCK_EVENT_BODY,
    MOCK_EVENT_BODY,
)
from utils.lambda_exceptions import CreateDocumentRefException
from utils.lambda_response import ApiGatewayResponse

TEST_DOCUMENT_LOCATION_ARF = f"s3://{MOCK_LG_STAGING_STORE_BUCKET}/{TEST_OBJECT_KEY}"
TEST_DOCUMENT_LOCATION_LG = f"s3://{MOCK_LG_STAGING_STORE_BUCKET}/{TEST_OBJECT_KEY}"


class MockError(Enum):
    Error = {
        "message": "Client error",
        "err_code": "AB_XXXX",
        "interaction_id": "88888888-4444-4444-4444-121212121212",
    }


@pytest.fixture
def both_type_event():
    return {"httpMethod": "POST", "body": json.dumps(MOCK_EVENT_BODY)}


@pytest.fixture
def arf_type_event():
    return {"httpMethod": "POST", "body": json.dumps(ARF_MOCK_EVENT_BODY)}


@pytest.fixture
def lg_type_event():
    return {"httpMethod": "POST", "body": json.dumps(LG_MOCK_EVENT_BODY)}


@pytest.fixture
def mock_processing_event_details(mocker):
    yield mocker.patch(
        "handlers.create_document_reference_handler.processing_event_details",
        return_value=(TEST_NHS_NUMBER, ARF_FILE_LIST),
    )


def test_create_document_reference_valid_both_lg_and_arf_type_returns_200(
    set_env, both_type_event, context, mocker
):
    mock_service = mocker.patch(
        "handlers.create_document_reference_handler.CreateDocumentReferenceService",
    )
    mock_service.return_value.url_responses = LG_AND_ARF_MOCK_RESPONSE
    expected = ApiGatewayResponse(
        200, json.dumps(LG_AND_ARF_MOCK_RESPONSE), "POST"
    ).create_api_gateway_response()

    actual = lambda_handler(both_type_event, context)

    assert actual == expected


arf_environment_variables = ["STAGING_STORE_BUCKET_NAME"]
lg_environment_variables = ["LLOYD_GEORGE_BUCKET_NAME", "LLOYD_GEORGE_DYNAMODB_NAME"]


@pytest.mark.parametrize("environment_variable", arf_environment_variables)
def test_lambda_handler_missing_environment_variables_type_staging_returns_500(
    set_env,
    monkeypatch,
    arf_type_event,
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
    actual = lambda_handler(arf_type_event, context)
    assert expected == actual


def test_processing_event_details_missing_event_body_raise_error(invalid_id_event):
    with pytest.raises(CreateDocumentRefException):
        processing_event_details(invalid_id_event)


def test_processing_event_details_missing_subject_body_raise_error():
    invalid_event = {"httpMethod": "POST", "body": "some_text"}
    with pytest.raises(CreateDocumentRefException):
        processing_event_details(invalid_event)


def test_processing_event_details_missing_identifier_body_raise_error():
    invalid_event = {"httpMethod": "POST", "body": """{"subject": "some_text"}"""}
    with pytest.raises(CreateDocumentRefException):
        processing_event_details(invalid_event)


def test_processing_event_details_missing_value_body_raise_error():
    invalid_event = {
        "httpMethod": "POST",
        "body": """{"subject": {"some_text": "text"}}""",
    }
    with pytest.raises(CreateDocumentRefException):
        processing_event_details(invalid_event)


def test_processing_event_details_missing_content_body_raise_error():
    invalid_event = {
        "httpMethod": "POST",
        "body": """{"subject": {"identifier": {"value": "text"}}}""",
    }
    with pytest.raises(CreateDocumentRefException):
        processing_event_details(invalid_event)


def test_processing_event_details_missing_attachment_body_raise_error():
    invalid_event = {
        "httpMethod": "POST",
        "body": """{"subject": {"identifier": {"value": "text"}},  "content": [
        {"attachment": "text}}""",
    }
    with pytest.raises(CreateDocumentRefException):
        processing_event_details(invalid_event)


def test_processing_event_details_get_nhs_number_and_doc_list(arf_type_event):
    try:
        expected_nhs_number = TEST_NHS_NUMBER
        expected_doc_list = ARF_FILE_LIST
        actual_nhs_number, actual_doc_list = processing_event_details(arf_type_event)
        assert expected_nhs_number == actual_nhs_number
        assert expected_doc_list == actual_doc_list
    except CreateDocumentRefException:
        assert False, "test"


def test_lambda_handler_processing_event_details_raise_error(
    mocker, arf_type_event, context, set_env, mock_processing_event_details
):
    mock_processing_event_details.side_effect = CreateDocumentRefException(
        400, MockError.Error
    )
    expected = ApiGatewayResponse(
        400,
        json.dumps(MockError.Error.value),
        "POST",
    ).create_api_gateway_response()
    actual = lambda_handler(arf_type_event, context)
    assert expected == actual
    mock_processing_event_details.assert_called_with(arf_type_event)


def test_lambda_handler_service_raise_error(
    mocker, arf_type_event, context, set_env, mock_processing_event_details
):
    mock_processing_event_details.return_value = (TEST_NHS_NUMBER, ARF_FILE_LIST)

    mock_service = mocker.patch(
        "services.create_document_reference_service.CreateDocumentReferenceService.create_document_reference_request",
        side_effect=CreateDocumentRefException(400, MockError.Error),
    )
    expected = ApiGatewayResponse(
        400,
        json.dumps(MockError.Error.value),
        "POST",
    ).create_api_gateway_response()
    actual = lambda_handler(arf_type_event, context)
    assert expected == actual
    mock_service.assert_called_with(TEST_NHS_NUMBER, ARF_FILE_LIST)
    mock_processing_event_details.assert_called_with(arf_type_event)


def test_lambda_handler_valid(
    mocker, arf_type_event, context, set_env, mock_processing_event_details
):
    mock_processing_event_details.return_value = (TEST_NHS_NUMBER, ARF_FILE_LIST)

    mock_service = mocker.patch(
        "handlers.create_document_reference_handler.CreateDocumentReferenceService",
    )
    mock_service.return_value.url_responses = ARF_MOCK_RESPONSE

    expected = ApiGatewayResponse(
        200,
        json.dumps(ARF_MOCK_RESPONSE),
        "POST",
    ).create_api_gateway_response()
    actual = lambda_handler(arf_type_event, context)
    assert expected == actual
    mock_processing_event_details.assert_called_with(arf_type_event)
