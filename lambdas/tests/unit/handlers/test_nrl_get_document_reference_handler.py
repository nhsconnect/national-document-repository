import json

import pytest
from enums.lambda_error import LambdaError
from handlers.nrl_get_document_reference_handler import lambda_handler
from tests.unit.conftest import TEST_UUID
from utils.lambda_exceptions import NRLGetDocumentReferenceException

MOCK_VALID_EVENT = {
    "httpMethod": "GET",
    "headers": {
        "Authorization": f"Bearer {TEST_UUID}",
    },
    "pathParameters": {"id": TEST_UUID},
    "body": None,
}


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


def test_lambda_handler_error(set_env, mock_service, context):
    expected_exception = {
        "resourceType": "OperationOutcome",
        "issue": [{"severity": "error", "code": "AB_XXXX", "details": "Client error"}],
    }
    mock_service.handle_get_document_reference_request.side_effect = (
        NRLGetDocumentReferenceException(400, LambdaError.MockError)
    )
    response = lambda_handler(MOCK_VALID_EVENT, context)
    assert response["statusCode"] == 400
    assert response["body"] == json.dumps(expected_exception)
