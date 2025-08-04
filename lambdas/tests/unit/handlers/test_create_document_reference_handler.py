import json
from enum import Enum

import pytest
from enums.lambda_error import LambdaError
from handlers.create_document_reference_handler import (
    lambda_handler,
    processing_event_details,
)
from services.create_document_reference_service import CreateDocumentReferenceService
from tests.unit.conftest import MOCK_STAGING_STORE_BUCKET, TEST_NHS_NUMBER, TEST_UUID
from tests.unit.helpers.data.create_document_reference import (
    ARF_FILE_LIST,
    MOCK_EVENT_BODY,
    ARF_MOCK_EVENT_BODY,
    LG_MOCK_EVENT_BODY,
    ARF_MOCK_RESPONSE,
    LG_AND_ARF_MOCK_RESPONSE,
    LG_MOCK_RESPONSE,
    UPLOAD_FEATURE_FLAG_DISABLED_MOCK_RESPONSE,
    NON_GP_ADMIN_OR_CLINICIAN_ROLE_MOCK_RESPONSE
)
from utils.exceptions import InvalidNhsNumberException, PatientNotFoundException
from utils.lambda_exceptions import CreateDocumentRefException, SearchPatientException
from utils.lambda_response import ApiGatewayResponse

TEST_DOCUMENT_LOCATION_ARF = f"s3://{MOCK_STAGING_STORE_BUCKET}/{TEST_UUID}"
TEST_DOCUMENT_LOCATION_LG = f"s3://{MOCK_STAGING_STORE_BUCKET}/{TEST_UUID}"

INVALID_NHS_NUMBER = "12345"

arf_environment_variables = ["STAGING_STORE_BUCKET_NAME"]
lg_environment_variables = ["LLOYD_GEORGE_BUCKET_NAME", "LLOYD_GEORGE_DYNAMODB_NAME"]

class MockError(Enum):
    Error = {
        "message": "Client error",
        "err_code": "AB_XXXX",
        "interaction_id": "88888888-4444-4444-4444-121212121212",
    }


@pytest.fixture
def both_type_event():
    return {
        "httpMethod": "POST",
        "body": json.dumps(MOCK_EVENT_BODY),
        "queryStringParameters": {"patientId": TEST_NHS_NUMBER},
    }


@pytest.fixture
def arf_type_event():
    return {
        "httpMethod": "POST",
        "body": json.dumps(ARF_MOCK_EVENT_BODY),
        "queryStringParameters": {"patientId": TEST_NHS_NUMBER},
    }


@pytest.fixture
def lg_type_event():
    return {
        "httpMethod": "POST",
        "body": json.dumps(LG_MOCK_EVENT_BODY),
        "queryStringParameters": {"patientId": TEST_NHS_NUMBER},
    }


@pytest.fixture
def mock_processing_event_details(mocker):
    yield mocker.patch(
        "handlers.create_document_reference_handler.processing_event_details",
        return_value=(TEST_NHS_NUMBER, ARF_FILE_LIST),
    )


@pytest.fixture
def mock_cdrService(mocker):
    mock_cdrService = mocker.MagicMock()
    mocker.patch(
        "handlers.create_document_reference_handler.CreateDocumentReferenceService",
        return_value=mock_cdrService,
    )
    yield mock_cdrService

@pytest.fixture
def mock_invalid_nhs_number_exception(mocker):
    mocker.patch("utils.decorators.validate_patient_id.validate_nhs_number", 
                 side_effect = InvalidNhsNumberException())


def test_create_document_reference_valid_both_lg_and_arf_type_returns_200(
    set_env, both_type_event, context, mock_cdrService, mock_upload_lambda_enabled
):
    mock_cdrService.create_document_reference_request.return_value = (
        LG_AND_ARF_MOCK_RESPONSE
    )
    expected = ApiGatewayResponse(
        200, json.dumps(LG_AND_ARF_MOCK_RESPONSE), "POST"
    ).create_api_gateway_response()

    actual = lambda_handler(both_type_event, context)

    assert actual == expected


def test_create_document_reference_valid_lg_type_returns_presigned_urls_and_200(
    set_env, lg_type_event, context, mock_cdrService, mock_upload_lambda_enabled
):
    mock_cdrService.create_document_reference_request.return_value = (
        LG_MOCK_RESPONSE
    )
    expected = ApiGatewayResponse(
        200, json.dumps(LG_MOCK_RESPONSE), "POST"
    ).create_api_gateway_response()
    actual = lambda_handler(lg_type_event, context)
    assert actual == expected


def test_create_document_reference_with_nhs_number_not_in_pds_returns_404(
    set_env, lg_type_event, context, mock_cdrService, mock_upload_lambda_enabled
):
    mock_cdrService.create_document_reference_request.side_effect = SearchPatientException(
        404, LambdaError.SearchPatientNoPDS)

    expected = ApiGatewayResponse(
        404, LambdaError.SearchPatientNoPDS, "POST"
    ).create_api_gateway_response()
    actual = lambda_handler(lg_type_event, context)
    assert actual == expected

def test_cdr_request_including_non_pdf_files_returns_400(
    set_env, lg_type_event, context, mock_cdrService, mock_upload_lambda_enabled
):
    mock_cdrService.create_document_reference_request.side_effect = CreateDocumentRefException(
        400, LambdaError.CreateDocFiles)
    
    expected = ApiGatewayResponse(
        400, LambdaError.CreateDocFiles, "POST"
    ).create_api_gateway_response()
    actual = lambda_handler(lg_type_event, context)
    assert actual == expected
    

def test_cdr_request_when_lgr_already_exists_returns_422(
    set_env, lg_type_event, context, mock_cdrService, mock_upload_lambda_enabled
):
    mock_cdrService.create_document_reference_request.side_effect = CreateDocumentRefException(
        422, LambdaError.CreateDocRecordAlreadyInPlace)
    
    expected = ApiGatewayResponse(
        422, LambdaError.CreateDocRecordAlreadyInPlace, "POST"
    ).create_api_gateway_response()
    actual = lambda_handler(lg_type_event, context)
    assert actual == expected

    mock_cdrService.create_document_reference_request.assert_called_once()


def test_cdr_request_when_lgr_is_in_process_of_uploading_returns_423(
    set_env, lg_type_event, context, mock_cdrService, mock_upload_lambda_enabled
):
    mock_cdrService.create_document_reference_request.side_effect = CreateDocumentRefException(
        423, LambdaError.UploadInProgressError)
    
    expected = ApiGatewayResponse(
        423, LambdaError.UploadInProgressError, "POST"
    ).create_api_gateway_response()
    actual = lambda_handler(lg_type_event, context)
    assert actual == expected

    mock_cdrService.create_document_reference_request.assert_called_once()
    

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
    mocker,
    arf_type_event,
    context,
    set_env,
    mock_processing_event_details,
    mock_upload_lambda_enabled,
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


def test_lambda_handler_valid(
    arf_type_event,
    context,
    set_env,
    mock_processing_event_details,
    mock_upload_lambda_enabled,
    mock_cdrService,
):
    mock_processing_event_details.return_value = (TEST_NHS_NUMBER, ARF_FILE_LIST)

    mock_cdrService.create_document_reference_request.return_value = ARF_MOCK_RESPONSE

    expected = ApiGatewayResponse(
        200,
        json.dumps(ARF_MOCK_RESPONSE),
        "POST",
    ).create_api_gateway_response()
    actual = lambda_handler(arf_type_event, context)
    assert expected == actual
    mock_processing_event_details.assert_called_with(arf_type_event)


def test_no_event_processing_when_upload_lambda_flag_disabled(
    set_env,
    lg_type_event,
    context,
    mock_processing_event_details,
    mock_upload_lambda_disabled,
):
    
    expected = ApiGatewayResponse(
        404, json.dumps(UPLOAD_FEATURE_FLAG_DISABLED_MOCK_RESPONSE), "POST"
    ).create_api_gateway_response()

    actual = lambda_handler(lg_type_event, context)

    assert expected == actual
    mock_processing_event_details.assert_not_called()

def test_invalid_nhs_number_returns_400(
    set_env, 
    lg_type_event, 
    context, 
    mock_invalid_nhs_number_exception,
    mock_processing_event_details,
    mock_cdrService
):  
    
    expected = ApiGatewayResponse(
        400, LambdaError.PatientIdInvalid.create_error_body(
                {"number": TEST_NHS_NUMBER}), "POST").create_api_gateway_response()
    actual = lambda_handler(lg_type_event, context)

    assert actual == expected
    
    mock_processing_event_details.assert_not_called()
    mock_cdrService.assert_not_called()

def test_ods_code_not_in_pilot_returns_404(
    set_env,
    context,
    lg_type_event,
    mock_cdrService,
    mock_upload_lambda_enabled
):
    mock_cdrService.create_document_reference_request.side_effect = CreateDocumentRefException(
        404, LambdaError.CreateDocRefOdsCodeNotAllowed)
    
    expected = ApiGatewayResponse(
        404, LambdaError.CreateDocRefOdsCodeNotAllowed, "POST"
    ).create_api_gateway_response()
    actual = lambda_handler(lg_type_event, context)

    assert actual == expected

    mock_cdrService.create_document_reference_request.create_document_reference.assert_not_called()