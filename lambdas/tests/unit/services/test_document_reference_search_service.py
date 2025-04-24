import json
from json import JSONDecodeError
from unittest.mock import MagicMock, call

import pytest
from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from models.document_reference import DocumentReference
from pydantic import ValidationError
from services.document_reference_search_service import DocumentReferenceSearchService
from tests.unit.helpers.data.dynamo.dynamo_responses import MOCK_SEARCH_RESPONSE
from utils.common_query_filters import NotDeleted
from utils.exceptions import DynamoServiceException
from utils.lambda_exceptions import DocumentRefSearchException

MOCK_DOCUMENT_REFERENCE = [
    DocumentReference.model_validate(MOCK_SEARCH_RESPONSE["Items"][0])
]

MOCK_FILE_SIZE = 24000

EXPECTED_RESPONSE = {
    "created": "2024-01-01T12:00:00.000Z",
    "fileName": "document.csv",
    "virusScannerResult": "Clean",
    "id": "3d8683b9-1665-40d2-8499-6e8302d507ff",
    "fileSize": MOCK_FILE_SIZE,
}


@pytest.fixture
def mock_document_service(mocker, set_env):
    service = DocumentReferenceSearchService()
    mock_s3_service = mocker.patch.object(service, "s3_service")
    mocker.patch.object(mock_s3_service, "get_file_size", return_value=MOCK_FILE_SIZE)
    mocker.patch.object(service, "dynamo_service")
    mocker.patch.object(service, "fetch_documents_from_table_with_nhs_number")
    mocker.patch.object(service, "is_upload_in_process", return_value=False)
    return service


def test_get_document_references_raise_json_error_when_no_table_list(
    mock_document_service, monkeypatch
):
    monkeypatch.setenv("DYNAMODB_TABLE_LIST", "")
    with pytest.raises(JSONDecodeError):
        mock_document_service._get_table_names()


def test_get_document_references_raise_validation_error(
    mock_document_service, validation_error
):
    mock_document_service.fetch_documents_from_table_with_nhs_number.side_effect = (
        validation_error
    )
    with pytest.raises(ValidationError):
        mock_document_service._fetch_documents("111111111", "test_table", NotDeleted)


def test_get_document_references_raise_client_error(mock_document_service):
    mock_document_service.fetch_documents_from_table_with_nhs_number.side_effect = (
        ClientError(
            {
                "Error": {
                    "Code": "test",
                    "Message": "test",
                }
            },
            "test",
        )
    )
    with pytest.raises(ClientError):
        mock_document_service._fetch_documents("111111111", "test_table", NotDeleted)


def test_get_document_references_raise_dynamodb_error(mock_document_service):
    mock_document_service.fetch_documents_from_table_with_nhs_number.side_effect = (
        DynamoServiceException()
    )
    with pytest.raises(DynamoServiceException):
        mock_document_service._fetch_documents("111111111", "test_table", NotDeleted)


def test_get_document_references_dynamo_return_empty_response(mock_document_service):
    mock_document_service.fetch_documents_from_table_with_nhs_number.return_value = []
    expected_results = []

    actual = mock_document_service._fetch_documents(
        "111111111", "test_table", NotDeleted
    )

    assert actual == expected_results


def test_get_document_references_dynamo_return_successful_response_single_table(
    mock_document_service, monkeypatch
):
    monkeypatch.setenv("DYNAMODB_TABLE_LIST", json.dumps(["test_table"]))

    mock_document_service.fetch_documents_from_table_with_nhs_number.return_value = (
        MOCK_DOCUMENT_REFERENCE
    )
    expected_results = MOCK_DOCUMENT_REFERENCE
    actual = mock_document_service._fetch_documents(
        "111111111", "test_table", NotDeleted
    )

    assert actual == expected_results


def test_build_document_model_response(mock_document_service, monkeypatch):
    expected_results = [EXPECTED_RESPONSE]
    actual = mock_document_service._process_documents(MOCK_DOCUMENT_REFERENCE, False)

    assert actual == expected_results


def test_get_document_references_dynamo_return_successful_response_multiple_tables(
    mock_document_service, mocker
):
    mock_fetch_documents = mocker.MagicMock(return_value=MOCK_DOCUMENT_REFERENCE)
    mock_document_service._fetch_documents = mock_fetch_documents
    mock_document_service._validate_upload_status = mocker.MagicMock()
    mock_document_service._process_documents = mocker.MagicMock(
        return_value=[EXPECTED_RESPONSE]
    )
    expected_results = [EXPECTED_RESPONSE, EXPECTED_RESPONSE]

    actual = mock_document_service._search_tables_for_documents(
        "1111111111", ["table1", "table2"], False
    )

    assert actual == expected_results


def test_get_document_references_raise_error_when_upload_is_in_process(
    mock_document_service,
):
    mock_document_service.is_upload_in_process.return_value = True

    with pytest.raises(DocumentRefSearchException):
        mock_document_service._validate_upload_status(MOCK_DOCUMENT_REFERENCE)


def test_get_document_references_success(mock_document_service, mocker):
    mock_get_table_names = mocker.MagicMock(return_value=["table1", "table2"])
    mock_document_service._get_table_names = mock_get_table_names
    mock_search_document = mocker.MagicMock(return_value=[{"id": "123"}])
    mock_document_service._search_tables_for_documents = mock_search_document

    result = mock_document_service.get_document_references(
        "1234567890", return_fhir=False
    )

    assert result == [{"id": "123"}]
    mock_get_table_names.assert_called_once()
    mock_search_document.assert_called_once_with(
        "1234567890", ["table1", "table2"], False
    )


def test_get_document_references_exception(mock_document_service, mocker):
    mock_document_service._get_table_names = mocker.MagicMock(
        side_effect=DynamoServiceException
    )

    with pytest.raises(DocumentRefSearchException) as exc_info:
        mock_document_service.get_document_references("1234567890")

    assert exc_info.value.status_code == 500
    assert exc_info.value.error == LambdaError.DocRefClient


def test_search_tables_for_documents(mock_document_service, mocker):
    mock_fetch_document_method = mocker.MagicMock(return_value=MOCK_DOCUMENT_REFERENCE)
    mock_document_service._fetch_documents = mock_fetch_document_method
    mock_document_id = {"id": "123"}
    mock_process_document = mocker.MagicMock(return_value=[mock_document_id])
    mock_document_service._process_documents = mock_process_document

    result = mock_document_service._search_tables_for_documents(
        "1234567890", ["table1", "table2"], return_fhir=False
    )

    assert result == [mock_document_id, mock_document_id]
    mock_fetch_document_method.assert_has_calls(
        [
            call("1234567890", "table1", NotDeleted),
            call("1234567890", "table2", NotDeleted),
        ]
    )
    mock_process_document.assert_has_calls(
        [call(MOCK_DOCUMENT_REFERENCE, False), call(MOCK_DOCUMENT_REFERENCE, False)]
    )


def test_validate_upload_status_raises_exception(mock_document_service):
    mock_document_service.is_upload_in_process = MagicMock(return_value=True)

    with pytest.raises(DocumentRefSearchException) as exc_info:
        mock_document_service._validate_upload_status(MOCK_DOCUMENT_REFERENCE)

    assert exc_info.value.status_code == 423
    assert exc_info.value.error == LambdaError.UploadInProgressError


def test_process_documents_return_fhir(mock_document_service):
    mock_document_service.create_document_reference_fhir_response = MagicMock(
        return_value={"fhir": "response"}
    )

    result = mock_document_service._process_documents(
        MOCK_DOCUMENT_REFERENCE, return_fhir=True
    )

    assert result == [{"fhir": "response"}]
    mock_document_service.create_document_reference_fhir_response.assert_called_once()


# def test_process_documents_return_model(mock_document_service):
#     mock_document_service._build_document_model = MagicMock(return_value={"id": "123"})
#     mock_document_service.SearchDocumentReference = MagicMock()
#     mock_document_service.SearchDocumentReference.return_value.model_dump = MagicMock(
#         return_value={"id": "123"}
#     )
#
#     result = mock_document_service._process_documents(
#         MOCK_DOCUMENT_REFERENCE, return_fhir=False
#     )
#
#     assert result == [{"id": "123"}]
#     mock_document_service._build_document_model.assert_called_once()
