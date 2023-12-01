from datetime import datetime, timedelta

import pytest
from enums.s3_lifecycle_tags import S3LifecycleDays, S3LifecycleTags
from freezegun import freeze_time
from models.document_reference import DocumentReference
from tests.unit.conftest import (
    MOCK_ARF_TABLE_NAME,
    MOCK_LG_TABLE_NAME,
    MOCK_TABLE_NAME,
    TEST_NHS_NUMBER,
)
from tests.unit.helpers.data.dynamo_responses import (
    MOCK_EMPTY_RESPONSE,
    MOCK_SEARCH_RESPONSE,
)

from lambdas.services.document_service import DocumentService

MOCK_DOCUMENT = {
    "ID": "3d8683b9-1665-40d2-8499-6e8302d507ff",
    "ContentType": "type",
    "Created": "2023-08-23T13:38:04.095Z",
    "Deleted": "",
    "FileLocation": "s3://test_s3_bucket/test-key-123",
    "FileName": "document.csv",
    "NhsNumber": "9000000009",
    "VirusScannerResult": "Clean",
}


@pytest.fixture
def nhs_number():
    return "9000000009"


def test_returns_list_of_lg_document_references_when_results_are_returned(
    set_env, mocker
):
    mocker.patch("boto3.resource")
    service = DocumentService()

    mock_dynamo_table = mocker.patch.object(service.dynamodb, "Table")
    mock_dynamo_table.return_value.query.return_value = MOCK_SEARCH_RESPONSE

    results = service.fetch_available_document_references_by_type(TEST_NHS_NUMBER, "LG")

    mock_dynamo_table.assert_called_with(MOCK_LG_TABLE_NAME)

    assert len(results) == 3
    for result in results:
        assert isinstance(result, DocumentReference)


def test_returns_list_of_arf_document_references_when_results_are_returned(
    set_env, mocker
):
    mocker.patch("boto3.resource")
    service = DocumentService()

    mock_dynamo_table = mocker.patch.object(service.dynamodb, "Table")
    mock_dynamo_table.return_value.query.return_value = MOCK_SEARCH_RESPONSE

    results = service.fetch_available_document_references_by_type(
        TEST_NHS_NUMBER, "ARF"
    )

    mock_dynamo_table.assert_called_with(MOCK_ARF_TABLE_NAME)

    assert len(results) == 3
    for result in results:
        assert isinstance(result, DocumentReference)


def test_returns_list_of_both_type_document_references_when_results_are_returned(
    set_env, mocker
):
    mocker.patch("boto3.resource")
    service = DocumentService()

    mock_dynamo_table = mocker.patch.object(service.dynamodb, "Table")
    mock_dynamo_table.return_value.query.side_effect = [
        MOCK_SEARCH_RESPONSE,
        MOCK_SEARCH_RESPONSE,
    ]

    results = service.fetch_available_document_references_by_type(
        TEST_NHS_NUMBER, "ALL"
    )

    assert mock_dynamo_table.call_count == 2

    assert len(results) == 6
    for result in results:
        assert isinstance(result, DocumentReference)


def test_returns_list_of_both_type_document_references_when_only_one_result_is_returned(
    set_env, mocker
):
    mocker.patch("boto3.resource")
    service = DocumentService()

    mock_dynamo_table = mocker.patch.object(service.dynamodb, "Table")
    mock_dynamo_table.return_value.query.side_effect = [
        MOCK_SEARCH_RESPONSE,
        MOCK_EMPTY_RESPONSE,
    ]

    results = service.fetch_available_document_references_by_type(
        TEST_NHS_NUMBER, "ALL"
    )

    assert mock_dynamo_table.call_count == 2

    assert len(results) == 3
    for result in results:
        assert isinstance(result, DocumentReference)


def test_returns_empty_list_of_lg_document_references_when_no_results_are_returned(
    set_env, mocker
):
    mocker.patch("boto3.resource")
    service = DocumentService()

    mock_dynamo_table = mocker.patch.object(service.dynamodb, "Table")
    mock_dynamo_table.return_value.query.return_value = MOCK_EMPTY_RESPONSE

    result = service.fetch_available_document_references_by_type(TEST_NHS_NUMBER, "LG")

    mock_dynamo_table.assert_called_with(MOCK_LG_TABLE_NAME)

    assert len(result) == 0


def test_returns_empty_list_when_invalid_doctype_supplied(set_env, mocker):
    mocker.patch("boto3.resource")
    service = DocumentService()

    result = service.fetch_available_document_references_by_type(
        TEST_NHS_NUMBER, "INVALID"
    )

    assert len(result) == 0


@freeze_time("2023-10-1 13:00:00")
def test_delete_documents_soft_delete(set_env, mocker):
    mocker.patch("boto3.client")

    test_doc_ref = DocumentReference.model_validate(MOCK_DOCUMENT)

    test_date = datetime.now()
    ttl_date = test_date + timedelta(days=float(S3LifecycleDays.SOFT_DELETE))

    test_update_fields = {
        "Deleted": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "TTL": int(ttl_date.timestamp()),
    }

    document_service = DocumentService()

    mock_create_object_tag = mocker.patch.object(
        document_service.s3_service, "create_object_tag"
    )
    mock_update_item = mocker.patch.object(document_service, "update_item")

    document_service.delete_documents(
        MOCK_TABLE_NAME, [test_doc_ref], str(S3LifecycleTags.SOFT_DELETE.value)
    )

    mock_create_object_tag.assert_called_once_with(
        file_key=test_doc_ref.get_file_key(),
        s3_bucket_name=test_doc_ref.get_file_bucket(),
        tag_key="soft-delete",
        tag_value="true",
    )

    mock_update_item.assert_called_once_with(
        MOCK_TABLE_NAME, test_doc_ref.id, updated_fields=test_update_fields
    )


@freeze_time("2023-10-1 13:00:00")
def test_delete_documents_death_delete(set_env, mocker):
    mocker.patch("boto3.client")

    test_doc_ref = DocumentReference.model_validate(MOCK_DOCUMENT)

    test_date = datetime.now()
    ttl_date = test_date + timedelta(days=float(S3LifecycleDays.DEATH_DELETE))

    test_update_fields = {
        "Deleted": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "TTL": int(ttl_date.timestamp()),
    }

    document_service = DocumentService()

    mock_create_object_tag = mocker.patch.object(
        document_service.s3_service, "create_object_tag"
    )
    mock_update_item = mocker.patch.object(document_service, "update_item")

    document_service.delete_documents(
        MOCK_TABLE_NAME, [test_doc_ref], str(S3LifecycleTags.DEATH_DELETE.value)
    )

    mock_create_object_tag.assert_called_once_with(
        file_key=test_doc_ref.get_file_key(),
        s3_bucket_name=test_doc_ref.get_file_bucket(),
        tag_key="patient-death",
        tag_value="true",
    )

    mock_update_item.assert_called_once_with(
        MOCK_TABLE_NAME, test_doc_ref.id, updated_fields=test_update_fields
    )


@pytest.mark.parametrize(
    ["doc_type", "table_name"],
    [("ARF", MOCK_ARF_TABLE_NAME), ("LG", MOCK_LG_TABLE_NAME)],
)
def test_delete_documents_by_type(set_env, mocker, doc_type, table_name):
    document_service = DocumentService()
    mock_delete_document = mocker.patch.object(DocumentService, "delete_documents")

    test_doc_ref = DocumentReference.model_validate(MOCK_DOCUMENT)

    document_service.delete_documents_by_type(
        doc_type, [test_doc_ref], str(S3LifecycleTags.SOFT_DELETE.value)
    )

    mock_delete_document.assert_called_once_with(
        table_name=table_name,
        document_references=[test_doc_ref],
        type_of_delete=str(S3LifecycleTags.SOFT_DELETE.value),
    )
