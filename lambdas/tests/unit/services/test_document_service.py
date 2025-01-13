from datetime import datetime, timedelta
from unittest.mock import call

import pytest
from enums.document_retention import DocumentRetentionDays
from enums.dynamo_filter import AttributeOperator
from enums.metadata_field_names import DocumentReferenceMetadataFields
from enums.supported_document_types import SupportedDocumentTypes
from freezegun import freeze_time
from models.document_reference import DocumentReference
from services.document_service import DocumentService
from tests.unit.conftest import (
    MOCK_ARF_TABLE_NAME,
    MOCK_LG_TABLE_NAME,
    MOCK_TABLE_NAME,
    TEST_NHS_NUMBER,
)
from tests.unit.helpers.data.dynamo.dynamo_responses import (
    MOCK_EMPTY_RESPONSE,
    MOCK_SEARCH_RESPONSE,
)
from tests.unit.helpers.data.test_documents import (
    create_test_lloyd_george_doc_store_refs,
)
from utils.dynamo_query_filter_builder import DynamoQueryFilterBuilder
from utils.exceptions import DocumentServiceException

MOCK_DOCUMENT = MOCK_SEARCH_RESPONSE["Items"][0]


@pytest.fixture
def mock_service(set_env, mocker):
    mocker.patch("boto3.resource")
    service = DocumentService()
    mocker.patch.object(service, "s3_service")
    mocker.patch.object(service, "dynamo_service")
    yield service


@pytest.fixture
def mock_dynamo_service(mocker, mock_service):
    mocker.patch.object(mock_service.dynamo_service, "query_table_by_index")
    mocker.patch.object(mock_service.dynamo_service, "update_item")
    yield mock_service.dynamo_service


@pytest.fixture
def mock_s3_service(mocker, mock_service):
    mocker.patch.object(mock_service.s3_service, "create_object_tag")
    yield mock_service.s3_service


@pytest.fixture
def mock_filter_expression():
    filter_builder = DynamoQueryFilterBuilder()
    filter_expression = filter_builder.add_condition(
        attribute=str(DocumentReferenceMetadataFields.DELETED.value),
        attr_operator=AttributeOperator.EQUAL,
        filter_value="",
    ).build()
    yield filter_expression


def test_fetch_available_document_references_by_type_lg_returns_list_of_doc_references(
    mock_service, mock_dynamo_service, mock_filter_expression
):
    mock_dynamo_service.query_table_by_index.return_value = MOCK_SEARCH_RESPONSE

    results = mock_service.fetch_available_document_references_by_type(
        TEST_NHS_NUMBER, SupportedDocumentTypes.LG, mock_filter_expression
    )

    assert len(results) == 3
    for result in results:
        assert isinstance(result, DocumentReference)

    mock_dynamo_service.query_table_by_index.assert_called_once_with(
        table_name=MOCK_LG_TABLE_NAME,
        index_name="NhsNumberIndex",
        search_key="NhsNumber",
        search_condition=TEST_NHS_NUMBER,
        requested_fields=DocumentReferenceMetadataFields.list(),
        query_filter=mock_filter_expression,
    )


def test_fetch_available_document_references_by_type_arf_returns_list_of_doc_references(
    mock_service, mock_dynamo_service, mock_filter_expression
):
    mock_dynamo_service.query_table_by_index.return_value = MOCK_SEARCH_RESPONSE

    results = mock_service.fetch_available_document_references_by_type(
        TEST_NHS_NUMBER, SupportedDocumentTypes.ARF, mock_filter_expression
    )

    assert len(results) == 3
    for result in results:
        assert isinstance(result, DocumentReference)

    mock_dynamo_service.query_table_by_index.assert_called_once_with(
        table_name=MOCK_ARF_TABLE_NAME,
        index_name="NhsNumberIndex",
        search_key="NhsNumber",
        search_condition=TEST_NHS_NUMBER,
        requested_fields=DocumentReferenceMetadataFields.list(),
        query_filter=mock_filter_expression,
    )


def test_fetch_available_document_references_by_type_lg_returns_empty_list_of_doc_references(
    mock_service, mock_dynamo_service, mock_filter_expression
):
    mock_dynamo_service.query_table_by_index.return_value = MOCK_EMPTY_RESPONSE

    result = mock_service.fetch_available_document_references_by_type(
        TEST_NHS_NUMBER, SupportedDocumentTypes.LG, mock_filter_expression
    )
    assert len(result) == 0
    mock_dynamo_service.query_table_by_index.assert_called_once_with(
        table_name=MOCK_LG_TABLE_NAME,
        index_name="NhsNumberIndex",
        search_key="NhsNumber",
        search_condition=TEST_NHS_NUMBER,
        requested_fields=DocumentReferenceMetadataFields.list(),
        query_filter=mock_filter_expression,
    )


def test_fetch_documents_from_table_with_filter_returns_list_of_doc_references(
    mocker, mock_service, mock_dynamo_service, mock_filter_expression
):
    expected_calls = [
        mocker.call(
            table_name=MOCK_LG_TABLE_NAME,
            index_name="NhsNumberIndex",
            search_key="NhsNumber",
            search_condition=TEST_NHS_NUMBER,
            requested_fields=DocumentReferenceMetadataFields.list(),
            query_filter=mock_filter_expression,
        )
    ]

    mock_dynamo_service.query_table_by_index.return_value = MOCK_SEARCH_RESPONSE

    results = mock_service.fetch_documents_from_table_with_filter(
        nhs_number=TEST_NHS_NUMBER,
        table=MOCK_LG_TABLE_NAME,
        query_filter=mock_filter_expression,
    )

    assert len(results) == 3
    for result in results:
        assert isinstance(result, DocumentReference)

    mock_dynamo_service.query_table_by_index.assert_has_calls(
        expected_calls, any_order=True
    )


def test_fetch_documents_from_table_with_filter_returns_empty_list_of_doc_references(
    mocker, mock_service, mock_dynamo_service, mock_filter_expression
):
    expected_calls = [
        mocker.call(
            table_name=MOCK_LG_TABLE_NAME,
            index_name="NhsNumberIndex",
            search_key="NhsNumber",
            search_condition=TEST_NHS_NUMBER,
            requested_fields=DocumentReferenceMetadataFields.list(),
            query_filter=mock_filter_expression,
        )
    ]
    mock_dynamo_service.query_table_by_index.return_value = MOCK_EMPTY_RESPONSE

    results = mock_service.fetch_documents_from_table_with_filter(
        nhs_number=TEST_NHS_NUMBER,
        table=MOCK_LG_TABLE_NAME,
        query_filter=mock_filter_expression,
    )

    assert len(results) == 0

    mock_dynamo_service.query_table_by_index.assert_has_calls(
        expected_calls, any_order=True
    )


@freeze_time("2023-10-1 13:00:00")
def test_delete_documents_soft_delete(
    mock_service, mock_dynamo_service, mock_s3_service
):
    test_doc_ref = DocumentReference.model_validate(MOCK_DOCUMENT)

    test_date = datetime.now()
    ttl_date = test_date + timedelta(days=float(DocumentRetentionDays.SOFT_DELETE))

    test_update_fields = {
        "Deleted": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "TTL": int(ttl_date.timestamp()),
    }

    mock_service.delete_document_references(
        MOCK_TABLE_NAME, [test_doc_ref], DocumentRetentionDays.SOFT_DELETE
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
    ttl_date = test_date + timedelta(days=float(DocumentRetentionDays.DEATH))

    test_update_fields = {
        "Deleted": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "TTL": int(ttl_date.timestamp()),
    }

    mock_service.delete_document_references(
        MOCK_TABLE_NAME, [test_doc_ref], DocumentRetentionDays.DEATH
    )

    mock_dynamo_service.update_item.assert_called_once_with(
        MOCK_TABLE_NAME, test_doc_ref.id, updated_fields=test_update_fields
    )


def test_update_documents(mock_service, mock_dynamo_service):
    test_doc_ref = DocumentReference.model_validate(MOCK_DOCUMENT)

    test_update_fields = {
        "TestField": "test",
    }

    update_item_call = call(
        MOCK_TABLE_NAME, test_doc_ref.id, updated_fields=test_update_fields
    )

    mock_service.update_documents(
        MOCK_TABLE_NAME, [test_doc_ref, test_doc_ref], test_update_fields
    )

    mock_dynamo_service.update_item.assert_has_calls(
        [update_item_call, update_item_call]
    )


def test_hard_delete_metadata_records(mock_service, mock_dynamo_service):
    test_doc_refs = [
        DocumentReference.model_validate(mock_document)
        for mock_document in MOCK_SEARCH_RESPONSE["Items"][:2]
    ]
    expected_deletion_keys = [
        {DocumentReferenceMetadataFields.ID.value: doc_ref.id}
        for doc_ref in test_doc_refs
    ]

    mock_service.hard_delete_metadata_records(MOCK_TABLE_NAME, test_doc_refs)

    mock_dynamo_service.delete_item.assert_has_calls(
        [
            call(MOCK_TABLE_NAME, expected_deletion_keys[0]),
            call(MOCK_TABLE_NAME, expected_deletion_keys[1]),
        ]
    )


@freeze_time("2023-10-30T10:25:00")
def test_check_existing_lloyd_george_records_return_true_if_upload_in_progress(
    mock_service,
):
    two_minutes_ago = 1698661380  # 2023-10-30T10:23:00
    mock_records_upload_in_process = create_test_lloyd_george_doc_store_refs(
        override={"uploaded": False, "uploading": True, "last_updated": two_minutes_ago}
    )

    response = mock_service.is_upload_in_process(mock_records_upload_in_process)

    assert response


def test_delete_document_object_successfully_deletes_s3_object(mock_service, caplog):
    test_bucket = "test-s3-bucket"
    test_file_key = "9000000000/test-file.pdf"

    expected_log_message = f"Located file `{test_file_key}` in `{test_bucket}`, attempting S3 object deletion"

    mock_service.s3_service.file_exist_on_s3.side_effect = [
        True,
        False,
    ]

    mock_service.delete_document_object(bucket=test_bucket, key=test_file_key)

    assert mock_service.s3_service.file_exist_on_s3.call_count == 2
    mock_service.s3_service.file_exist_on_s3.assert_called_with(
        s3_bucket_name=test_bucket, file_key=test_file_key
    )
    mock_service.s3_service.delete_object.assert_called_with(
        s3_bucket_name=test_bucket, file_key=test_file_key
    )

    assert expected_log_message in caplog.records[-1].msg


def test_delete_document_object_fails_to_delete_s3_object(mock_service, caplog):
    test_bucket = "test-s3-bucket"
    test_file_key = "9000000000/test-file.pdf"

    expected_err_msg = "Document located in S3 after deletion"

    mock_service.s3_service.file_exist_on_s3.side_effect = [
        True,
        True,
    ]

    with pytest.raises(DocumentServiceException) as e:
        mock_service.delete_document_object(bucket=test_bucket, key=test_file_key)

    assert mock_service.s3_service.file_exist_on_s3.call_count == 2
    mock_service.s3_service.file_exist_on_s3.assert_called_with(
        s3_bucket_name=test_bucket, file_key=test_file_key
    )
    mock_service.s3_service.delete_object.assert_called_with(
        s3_bucket_name=test_bucket, file_key=test_file_key
    )
    assert expected_err_msg == str(e.value)
