import json
from copy import deepcopy

import pytest
from enums.lambda_error import LambdaError
from enums.snomed_codes import SnomedCodes
from handlers.get_fhir_document_reference_handler import (
    get_id_and_snomed_from_path_parameters,
    lambda_handler,
)
from models.document_reference import DocumentReference
from tests.unit.conftest import TEST_UUID
from unit.helpers.data.dynamo.dynamo_responses import MOCK_SEARCH_RESPONSE
from utils.lambda_exceptions import GetFhirDocumentReferenceException

SNOMED_CODE = SnomedCodes.LLOYD_GEORGE.value.code

MOCK_VALID_EVENT = {
    "httpMethod": "GET",
    "headers": {
        "Authorization": f"Bearer {TEST_UUID}",
        "cis2-urid": TEST_UUID,
    },
    "pathParameters": {"id": f"{SNOMED_CODE}~{TEST_UUID}"},
    "body": None,
}

MOCK_INVALID_EVENT_ID_MALFORMED = deepcopy(MOCK_VALID_EVENT)
MOCK_INVALID_EVENT_ID_MALFORMED["pathParameters"]["id"] = f"~{TEST_UUID}"

MOCK_EVENT_MISSING_ROLE_ID = deepcopy(MOCK_VALID_EVENT)
MOCK_EVENT_MISSING_ROLE_ID["headers"] = {"Authorization": f"Bearer {TEST_UUID}"}

MOCK_DOCUMENT_REFERENCE = DocumentReference.model_validate(
    MOCK_SEARCH_RESPONSE["Items"][0]
)


@pytest.fixture
def mock_oidc_service(mocker):
    mock_oidc = mocker.patch("handlers.get_fhir_document_reference_handler.OidcService")
    mock_oidc_instance = mock_oidc.return_value
    mock_oidc_instance.fetch_userinfo.return_value = {"user": "info"}
    mock_oidc_instance.fetch_user_org_code.return_value = "TEST_ORG"
    mock_oidc_instance.fetch_user_role_code.return_value = ("R8000", TEST_UUID)
    return mock_oidc_instance


@pytest.fixture
def mock_config_service(mocker):
    mock_config = mocker.patch(
        "handlers.get_fhir_document_reference_handler.DynamicConfigurationService"
    )
    mock_config_instance = mock_config.return_value
    return mock_config_instance


@pytest.fixture
def mock_document_service(mocker):
    mock_service = mocker.patch(
        "handlers.get_fhir_document_reference_handler.GetFhirDocumentReferenceService"
    )
    mock_service_instance = mock_service.return_value
    mock_service_instance.handle_get_document_reference_request.return_value = (
        MOCK_DOCUMENT_REFERENCE
    )
    return mock_service_instance


@pytest.fixture
def mock_search_patient_service(mocker):
    mock_service = mocker.patch(
        "handlers.get_fhir_document_reference_handler.SearchPatientDetailsService"
    )
    mock_service_instance = mock_service.return_value
    return mock_service_instance


def test_lambda_handler_happy_path(
    set_env,
    mock_oidc_service,
    mock_config_service,
    mock_document_service,
    mock_search_patient_service,
    context,
):
    mock_document_service.create_document_reference_fhir_response.return_value = (
        "test_document_reference",
        False,
    )
    response = lambda_handler(MOCK_VALID_EVENT, context)
    assert response["statusCode"] == 200
    assert response["body"] == "test_document_reference"

    # Verify correct method calls
    mock_oidc_service.fetch_userinfo.assert_called_once()
    mock_oidc_service.fetch_user_org_code.assert_called_once()
    mock_oidc_service.fetch_user_role_code.assert_called_once()
    mock_document_service.handle_get_document_reference_request.assert_called_once_with(
        SNOMED_CODE, TEST_UUID
    )
    mock_document_service.create_document_reference_fhir_response.assert_called_once_with(
        MOCK_DOCUMENT_REFERENCE
    )


def test_lambda_handler_empty_event(
    set_env, mock_oidc_service, mock_config_service, mock_document_service, context
):
    response = lambda_handler({}, context)
    assert response["statusCode"] == 400
    mock_document_service.handle_get_document_reference_request.assert_not_called()


def test_lambda_handler_missing_auth(
    set_env, mock_oidc_service, mock_config_service, mock_document_service, context
):
    event_without_auth = deepcopy(MOCK_VALID_EVENT)
    event_without_auth["headers"] = {}

    response = lambda_handler(event_without_auth, context)
    assert response["statusCode"] == 401
    mock_document_service.handle_get_document_reference_request.assert_not_called()


def test_lambda_handler_missing_role_id(
    set_env,
    mock_oidc_service,
    mock_config_service,
    mock_document_service,
    context,
    mock_search_patient_service,
):
    mock_document_service.create_document_reference_fhir_response.return_value = (
        "test_document_reference",
        False,
    )

    response = lambda_handler(MOCK_EVENT_MISSING_ROLE_ID, context)

    # The handler should still work without cis2-urid, using a default role
    assert response["statusCode"] == 200
    mock_document_service.handle_get_document_reference_request.assert_called_once()


def test_lambda_handler_id_malformed(
    set_env, mock_oidc_service, mock_config_service, mock_document_service, context
):
    response = lambda_handler(MOCK_INVALID_EVENT_ID_MALFORMED, context)
    assert response["statusCode"] == 404
    mock_document_service.handle_get_document_reference_request.assert_not_called()


def test_lambda_handler_oidc_error(set_env, mock_config_service, context, mocker):
    # Test when OIDC service setup fails
    mocker.patch(
        "handlers.get_fhir_document_reference_handler.OidcService.set_up_oidc_parameters",
        side_effect=GetFhirDocumentReferenceException(500, LambdaError.MockError),
    )

    response = lambda_handler(MOCK_VALID_EVENT, context)
    assert response["statusCode"] == 500
    response_body = json.loads(response["body"])
    assert response_body["issue"][0]["diagnostics"] == "Client error"


def test_lambda_handler_invalid_path_parameters(
    set_env, mock_oidc_service, mock_config_service, mock_document_service, context
):
    event_with_invalid_path = deepcopy(MOCK_VALID_EVENT)
    event_with_invalid_path["pathParameters"] = {"id": "invalid_format_no_tilde"}

    response = lambda_handler(event_with_invalid_path, context)
    assert response["statusCode"] == 404
    mock_document_service.handle_get_document_reference_request.assert_not_called()


@pytest.mark.parametrize(
    "error_status_code, lambda_error",
    [
        (404, LambdaError.DocumentReferenceNotFound),
        (403, LambdaError.DocumentReferenceForbidden),
        (400, LambdaError.DocumentReferenceInvalidRequest),
        (500, LambdaError.DocumentReferenceGeneralError),
    ],
)
def test_lambda_handler_service_errors(
    set_env,
    mock_oidc_service,
    mock_config_service,
    mock_document_service,
    context,
    error_status_code,
    lambda_error,
):
    mock_document_service.handle_get_document_reference_request.side_effect = (
        GetFhirDocumentReferenceException(error_status_code, lambda_error)
    )

    response = lambda_handler(MOCK_VALID_EVENT, context)
    assert response["statusCode"] == error_status_code

    response_body = json.loads(response["body"])
    assert response_body["resourceType"] == "OperationOutcome"
    assert (
        response_body["issue"][0]["details"]["coding"][0]["code"]
        == lambda_error.value.get("fhir_coding").code()
    )
    assert (
        response_body["issue"][0]["details"]["coding"][0]["display"]
        == lambda_error.value.get("fhir_coding").display()
    )
    assert response_body["issue"][0]["diagnostics"] == lambda_error.value.get("message")


def test_get_id_and_snomed_from_path_parameters():
    path_parameter = f"{SNOMED_CODE}~{TEST_UUID}"

    document_id, snomed = get_id_and_snomed_from_path_parameters(path_parameter)
    assert document_id == TEST_UUID
    assert snomed == SNOMED_CODE


def test_get_id_and_snomed_from_path_parameters_no_tilde():
    document_id, snomed = get_id_and_snomed_from_path_parameters("notildePresent")
    assert document_id is None
    assert snomed is None


def test_get_id_and_snomed_from_path_parameters_extra_tildes():
    # Test with extra tildes
    path_parameter = f"{SNOMED_CODE}~{TEST_UUID}~extra"

    document_id, snomed = get_id_and_snomed_from_path_parameters(path_parameter)
    assert document_id is None
    assert snomed is None


def test_get_id_and_snomed_from_path_parameters_empty():
    document_id, snomed = get_id_and_snomed_from_path_parameters("")
    assert document_id is None
    assert snomed is None


def test_lambda_handler_oidc_auth_exception(
    set_env, mock_config_service, context, mocker
):
    # Test when OIDC authentication fails
    mock_oidc = mocker.patch("handlers.get_fhir_document_reference_handler.OidcService")
    mock_oidc_instance = mock_oidc.return_value
    mock_oidc_instance.fetch_userinfo.side_effect = Exception("Auth failed")

    response = lambda_handler(MOCK_VALID_EVENT, context)
    assert response["statusCode"] == 500


# def test_lambda_handler_ssm_initialization(
#     set_env, mock_config_service, context, mocker, mock_document_service
# ):
#     mock_document_service.create_document_reference_fhir_response.return_value = ("test_document_reference", False)
#
#     # Test the SSM initialisation part
#     mock_ssm = mocker.patch("handlers.get_fhir_document_reference_handler.SSMService")
#     mock_web_client = mocker.patch(
#         "handlers.get_fhir_document_reference_handler.WebApplicationClient"
#     )
#     mock_oidc = mocker.patch("handlers.get_fhir_document_reference_handler.OidcService")
#     mock_oidc_instance = mock_oidc.return_value
#     mock_oidc_instance.fetch_userinfo.return_value = {"user": "info"}
#     mock_oidc_instance.fetch_user_org_code.return_value = "TEST_ORG"
#     mock_oidc_instance.fetch_user_role_code.return_value = ("R8000", TEST_UUID)
#
#     mock_document_service = mocker.patch(
#         "handlers.get_fhir_document_reference_handler.GetFhirDocumentReferenceService"
#     )
#     mock_service_instance = mock_document_service.return_value
#     mock_service_instance.handle_get_document_reference_request.return_value = (
#         "test_document_reference"
#     )
#
#     response = lambda_handler(MOCK_VALID_EVENT, context)
#     assert response["statusCode"] == 200
#
#     # Verify SSM initialization
#     mock_oidc_instance.set_up_oidc_parameters.assert_called_once_with(
#         mock_ssm, mock_web_client
#     )
