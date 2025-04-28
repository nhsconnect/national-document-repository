import json
from unittest.mock import patch

import pytest
from handlers.fhir_document_reference_search_handler import lambda_handler


@pytest.fixture
def valid_nhs_number_event():
    return {
        "queryStringParameters": {"patientId": "9000000009"},
        "headers": {"Authorization": "Bearer valid-token"},
    }


@pytest.fixture
def invalid_nhs_number_event():
    return {
        "queryStringParameters": {"patientId": "invalid-nhs-number"},
        "headers": {"Authorization": "Bearer valid-token"},
    }


@pytest.fixture
def missing_nhs_number_event():
    return {
        "queryStringParameters": {},
        "headers": {"Authorization": "Bearer valid-token"},
    }


@pytest.fixture
def mock_document_reference_search_service():
    with patch(
        "handlers.get_document_references_handler.DocumentReferenceSearchService"
    ) as mock_service:
        service_instance = mock_service.return_value
        yield service_instance


def test_lambda_handler_returns_200_with_documents(
    mock_document_reference_search_service, valid_nhs_number_event, context, set_env
):
    mock_document_references = [
        {"resourceType": "DocumentReference", "status": "current"},
        {"resourceType": "DocumentReference", "status": "current"},
    ]
    mock_document_reference_search_service.get_document_references.return_value = (
        mock_document_references
    )

    response = lambda_handler(valid_nhs_number_event, context)

    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == mock_document_references
    mock_document_reference_search_service.get_document_references.assert_called_once_with(
        nhs_number="9000000009", return_fhir=True
    )


def test_lambda_handler_returns_204_when_no_documents(
    mock_document_reference_search_service, valid_nhs_number_event, context, set_env
):
    mock_document_reference_search_service.get_document_references.return_value = []

    response = lambda_handler(valid_nhs_number_event, context)

    assert response["statusCode"] == 204
    assert json.loads(response["body"]) == []
    mock_document_reference_search_service.get_document_references.assert_called_once_with(
        nhs_number="9000000009", return_fhir=True
    )


def test_lambda_handler_returns_500_for_invalid_nhs_number(
    mock_document_reference_search_service, invalid_nhs_number_event, context, set_env
):
    response = lambda_handler(invalid_nhs_number_event, context)

    assert response["statusCode"] == 500

    mock_document_reference_search_service.get_document_references.assert_not_called()


def test_lambda_handler_returns_500_for_missing_nhs_number(
    mock_document_reference_search_service, missing_nhs_number_event, context, set_env
):
    response = lambda_handler(missing_nhs_number_event, context)

    assert response["statusCode"] == 500

    mock_document_reference_search_service.get_document_references.assert_not_called()
