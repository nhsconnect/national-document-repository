from datetime import datetime, timedelta

import pytest
from enums.metadata_field_names import DocumentReferenceMetadataFields
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
def mock_service(set_env, mocker):
    mocker.patch("boto3.resource")
    service = DocumentService()
    mocker.patch.object(service, "s3_service")
    mocker.patch.object(service, "dynamo_service")
    yield service


@pytest.fixture
def mock_dynamo_service(mocker, mock_service):
    mocker.patch.object(mock_service.dynamo_service, "query_with_requested_fields")
    mocker.patch.object(mock_service.dynamo_service, "update_item")
    yield mock_service.dynamo_service


@pytest.fixture
def mock_s3_service(mocker, mock_service):
    mocker.patch.object(mock_service.s3_service, "create_object_tag")
    yield mock_service.s3_service


def test_fetch_available_document_references_by_type_lg_returns_list_of_doc_references(
    mock_service, mock_dynamo_service
):
    mock_dynamo_service.query_with_requested_fields.return_value = MOCK_SEARCH_RESPONSE

    results = mock_service.fetch_available_document_references_by_type(
        TEST_NHS_NUMBER, "LG"
    )

    assert len(results) == 3
    for result in results:
        assert isinstance(result, DocumentReference)

    mock_dynamo_service.query_with_requested_fields.assert_called_once_with(
        table_name=MOCK_LG_TABLE_NAME,
        index_name="NhsNumberIndex",
        search_key="NhsNumber",
        search_condition=TEST_NHS_NUMBER,
        requested_fields=DocumentReferenceMetadataFields.list(),
        filtered_fields={DocumentReferenceMetadataFields.DELETED.value: ""},
    )


def test_fetch_available_document_references_by_type_arf_returns_list_of_doc_references(
    mock_service, mock_dynamo_service
):
    mock_dynamo_service.query_with_requested_fields.return_value = MOCK_SEARCH_RESPONSE

    results = mock_service.fetch_available_document_references_by_type(
        TEST_NHS_NUMBER, "ARF"
    )

    assert len(results) == 3
    for result in results:
        assert isinstance(result, DocumentReference)

    mock_dynamo_service.query_with_requested_fields.assert_called_once_with(
        table_name=MOCK_ARF_TABLE_NAME,
        index_name="NhsNumberIndex",
        search_key="NhsNumber",
        search_condition=TEST_NHS_NUMBER,
        requested_fields=DocumentReferenceMetadataFields.list(),
        filtered_fields={DocumentReferenceMetadataFields.DELETED.value: ""},
    )


def test_fetch_available_document_references_by_type_all_returns_list_of_doc_references(
    mocker, mock_service, mock_dynamo_service
):
    mock_dynamo_service.query_with_requested_fields.return_value = MOCK_SEARCH_RESPONSE

    results = mock_service.fetch_available_document_references_by_type(
        TEST_NHS_NUMBER, "ALL"
    )

    assert len(results) == 6
    for result in results:
        assert isinstance(result, DocumentReference)

    expected_calls = [
        mocker.call(
            table_name=MOCK_ARF_TABLE_NAME,
            index_name="NhsNumberIndex",
            search_key="NhsNumber",
            search_condition=TEST_NHS_NUMBER,
            requested_fields=DocumentReferenceMetadataFields.list(),
            filtered_fields={DocumentReferenceMetadataFields.DELETED.value: ""},
        ),
        mocker.call(
            table_name=MOCK_LG_TABLE_NAME,
            index_name="NhsNumberIndex",
            search_key="NhsNumber",
            search_condition=TEST_NHS_NUMBER,
            requested_fields=DocumentReferenceMetadataFields.list(),
            filtered_fields={DocumentReferenceMetadataFields.DELETED.value: ""},
        ),
    ]

    mock_dynamo_service.query_with_requested_fields.assert_has_calls(
        expected_calls, any_order=True
    )


def test_fetch_available_document_references_by_type_all_only_one_result_is_returned_returns_doc_references(
    mocker, mock_service, mock_dynamo_service
):
    mock_dynamo_service.query_with_requested_fields.side_effect = [
        MOCK_SEARCH_RESPONSE,
        MOCK_EMPTY_RESPONSE,
    ]

    results = mock_service.fetch_available_document_references_by_type(
        TEST_NHS_NUMBER, "ALL"
    )

    assert len(results) == 3
    for result in results:
        assert isinstance(result, DocumentReference)

    expected_calls = [
        mocker.call(
            table_name=MOCK_ARF_TABLE_NAME,
            index_name="NhsNumberIndex",
            search_key="NhsNumber",
            search_condition=TEST_NHS_NUMBER,
            requested_fields=DocumentReferenceMetadataFields.list(),
            filtered_fields={DocumentReferenceMetadataFields.DELETED.value: ""},
        ),
        mocker.call(
            table_name=MOCK_LG_TABLE_NAME,
            index_name="NhsNumberIndex",
            search_key="NhsNumber",
            search_condition=TEST_NHS_NUMBER,
            requested_fields=DocumentReferenceMetadataFields.list(),
            filtered_fields={DocumentReferenceMetadataFields.DELETED.value: ""},
        ),
    ]

    mock_dynamo_service.query_with_requested_fields.assert_has_calls(
        expected_calls, any_order=True
    )


def test_fetch_available_document_references_by_type_lg_returns_empty_list_of_doc_references(
    mock_service, mock_dynamo_service
):
    mock_dynamo_service.query_with_requested_fields.return_value = MOCK_EMPTY_RESPONSE

    result = mock_service.fetch_available_document_references_by_type(
        TEST_NHS_NUMBER, "LG"
    )

    assert len(result) == 0
    mock_dynamo_service.query_with_requested_fields.assert_called_once_with(
        table_name=MOCK_LG_TABLE_NAME,
        index_name="NhsNumberIndex",
        search_key="NhsNumber",
        search_condition=TEST_NHS_NUMBER,
        requested_fields=DocumentReferenceMetadataFields.list(),
        filtered_fields={DocumentReferenceMetadataFields.DELETED.value: ""},
    )


def test_fetch_available_document_references_by_type_when_invalid_doctype_supplied_returns_empty_list(
    mock_service, mock_dynamo_service
):
    result = mock_service.fetch_available_document_references_by_type(
        TEST_NHS_NUMBER, "INVALID"
    )

    assert len(result) == 0
    mock_dynamo_service.query_with_requested_fields.assert_not_called()


@freeze_time("2023-10-1 13:00:00")
def test_delete_documents_soft_delete(
    mock_service, mock_dynamo_service, mock_s3_service
):
    test_doc_ref = DocumentReference.model_validate(MOCK_DOCUMENT)

    test_date = datetime.now()
    ttl_date = test_date + timedelta(days=float(S3LifecycleDays.SOFT_DELETE))

    test_update_fields = {
        "Deleted": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "TTL": int(ttl_date.timestamp()),
    }

    mock_service.delete_documents(
        MOCK_TABLE_NAME, [test_doc_ref], str(S3LifecycleTags.SOFT_DELETE.value)
    )

    mock_s3_service.create_object_tag.assert_called_once_with(
        file_key=test_doc_ref.get_file_key(),
        s3_bucket_name=test_doc_ref.get_file_bucket(),
        tag_key="soft-delete",
        tag_value="true",
    )

    mock_dynamo_service.update_item.assert_called_once_with(
        MOCK_TABLE_NAME, test_doc_ref.id, updated_fields=test_update_fields
    )


@freeze_time("2023-10-1 13:00:00")
def test_delete_documents_death_delete(
    mock_service, mock_dynamo_service, mock_s3_service
):
    test_doc_ref = DocumentReference.model_validate(MOCK_DOCUMENT)

    test_date = datetime.now()
    ttl_date = test_date + timedelta(days=float(S3LifecycleDays.DEATH_DELETE))

    test_update_fields = {
        "Deleted": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "TTL": int(ttl_date.timestamp()),
    }

    mock_service.delete_documents(
        MOCK_TABLE_NAME, [test_doc_ref], str(S3LifecycleTags.DEATH_DELETE.value)
    )

    mock_s3_service.create_object_tag.assert_called_once_with(
        file_key=test_doc_ref.get_file_key(),
        s3_bucket_name=test_doc_ref.get_file_bucket(),
        tag_key="patient-death",
        tag_value="true",
    )

    mock_dynamo_service.update_item.assert_called_once_with(
        MOCK_TABLE_NAME, test_doc_ref.id, updated_fields=test_update_fields
    )
