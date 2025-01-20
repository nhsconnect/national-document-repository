import json
from copy import deepcopy

import pytest
from enums.lambda_error import LambdaError
from enums.snomed_codes import SnomedCodes
from handlers.nrl_get_document_reference_handler import (
    get_id_and_snomed_from_path_parameters,
    lambda_handler,
)
from tests.unit.conftest import TEST_UUID
from utils.lambda_exceptions import NRLGetDocumentReferenceException

MOCK_VALID_EVENT = {
    "httpMethod": "GET",
    "headers": {
        "Authorization": f"Bearer {TEST_UUID}",
    },
    "pathParameters": {"id": f"{SnomedCodes}~{TEST_UUID}"},
    "body": None,
}

MOCK_INVALID_EVENT_ID_MALFORMED = deepcopy(MOCK_VALID_EVENT)
MOCK_INVALID_EVENT_ID_MALFORMED["pathParameters"]["id"] = f"~{TEST_UUID}"


@pytest.fixture
def mock_service(mocker):
    mocked_class = mocker.patch(
        "handlers.nrl_get_document_reference_handler.NRLGetDocumentReferenceService"
    )
    mocker.patch(
        "handlers.nrl_get_document_reference_handler.DynamicConfigurationService"
    )
    mocked_instance = mocked_class.return_value
    mocked_class.return_value.handle_get_document_reference_request.return_value = (
        "test_document_reference"
    )
    return mocked_instance


def test_lambda_handler_happy_path(set_env, mock_service, context):
    response = lambda_handler(MOCK_VALID_EVENT, context)
    assert response["statusCode"] == 200


def test_lambda_handler_missing_id(set_env, mock_service, event, context):
    response = lambda_handler(event, context)
    assert response["statusCode"] == 400
    mock_service.handle_get_document_reference_request.assert_not_called()


def test_lambda_handler_empty_event(set_env, mock_service, event, context):
    response = lambda_handler({}, context)
    assert response["statusCode"] == 400
    mock_service.handle_get_document_reference_request.assert_not_called()


def test_lambda_handler_missing_auth(set_env, mock_service, event, context):
    response = lambda_handler(
        {"pathParameters": {"id": f"{SnomedCodes.LLOYD_GEORGE}~{TEST_UUID}"}}, context
    )
    assert response["statusCode"] == 401
    mock_service.handle_get_document_reference_request.assert_not_called()


def test_lambda_handler_id_malformed(set_env, mock_service, event, context):
    response = lambda_handler(MOCK_INVALID_EVENT_ID_MALFORMED, context)
    assert response["statusCode"] == 404
    mock_service.handle_get_document_reference_request.assert_not_called()


@pytest.mark.parametrize(
    "error_status_code, lambda_error",
    [
        ("404", LambdaError.DocumentReferenceNotFound),
        ("403", LambdaError.DocumentReferenceUnauthorised),
        ("403", LambdaError.DocumentReferenceInvalidRequest),
        ("400", LambdaError.DocumentReferenceGeneralError),
    ],
)
def test_lambda_handler_service_errors(
    set_env, mock_service, context, error_status_code, lambda_error
):
    expected_exception = {
        "resourceType": "OperationOutcome",
        "issue": [
            {
                "severity": "error",
                "code": "exception",
                "details": {
                    "coding": [
                        {
                            "system": "http://hl7.org/fhir/issue-type",
                            "code": lambda_error.value.get("fhir_coding").code(),
                            "display": lambda_error.value.get("fhir_coding").display(),
                        }
                    ],
                },
                "diagnostics": lambda_error.value.get("message"),
            }
        ],
    }

    mock_service.handle_get_document_reference_request.side_effect = (
        NRLGetDocumentReferenceException(error_status_code, lambda_error)
    )
    response = lambda_handler(MOCK_VALID_EVENT, context)
    assert response["statusCode"] == error_status_code
    assert json.loads(response["body"]) == expected_exception


def test_get_id_and_snomed_from_path(event, context):
    path_parameter = f"16521000000101~{TEST_UUID}"

    id, snomed = get_id_and_snomed_from_path_parameters(path_parameter)
    assert id == TEST_UUID
    assert snomed == "16521000000101"


def test_get_id_and_snomed_from_path_parameters_no_tilde_present(event, context):

    id, snomed = get_id_and_snomed_from_path_parameters("notildePresent ")
    assert id is None
    assert snomed is None
