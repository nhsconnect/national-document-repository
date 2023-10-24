import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import boto3
import pytest
from enums.s3_lifecycle_tags import S3LifecycleDays, S3LifecycleTags
from freezegun import freeze_time
from models.document_reference import DocumentReference
from tests.unit.conftest import MOCK_TABLE_NAME
from tests.unit.helpers.data.dynamo_responses import (MOCK_EMPTY_RESPONSE,
                                                      MOCK_SEARCH_RESPONSE)

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


def test_returns_list_of_documents_when_results_are_returned(nhs_number):
    expected_table = "expected_table_name"
    os.environ["LLOYD_GEORGE_DYNAMODB_NAME"] = expected_table
    os.environ["DOCUMENT_STORE_DYNAMODB_NAME"] = "no-table"

    with patch.object(boto3, "resource", return_value=MagicMock()) as mock_dynamo:
        mock_table = MagicMock()
        mock_dynamo.return_value.Table.return_value = mock_table
        mock_table.query.return_value = MOCK_SEARCH_RESPONSE
        result = DocumentService().fetch_available_document_references_by_type(
            nhs_number, "LG"
        )

        mock_dynamo.return_value.Table.assert_called_with(expected_table)

        assert len(result) == 3
        assert type(result[0]) == DocumentReference


def test_only_retrieves_documents_from_lloyd_george_table(nhs_number):
    expected_table = "expected_table_name"
    os.environ["LLOYD_GEORGE_DYNAMODB_NAME"] = expected_table
    os.environ["DOCUMENT_STORE_DYNAMODB_NAME"] = "no-table"

    with patch.object(boto3, "resource", return_value=MagicMock()) as mock_dynamo:
        mock_table = MagicMock()
        mock_dynamo.return_value.Table.return_value = mock_table
        mock_table.query.return_value = MOCK_EMPTY_RESPONSE
        result = DocumentService().fetch_available_document_references_by_type(
            nhs_number, "LG"
        )

        mock_dynamo.return_value.Table.assert_called_with(expected_table)

        assert len(result) == 0


def test_only_retrieves_documents_from_electronic_health_record_table(nhs_number):
    expected_table = "expected_table_name"
    os.environ["LLOYD_GEORGE_DYNAMODB_NAME"] = "no-table"
    os.environ["DOCUMENT_STORE_DYNAMODB_NAME"] = expected_table

    with patch.object(boto3, "resource", return_value=MagicMock()) as mock_dynamo:
        mock_table = MagicMock()
        mock_dynamo.return_value.Table.return_value = mock_table
        mock_table.query.return_value = MOCK_EMPTY_RESPONSE
        result = DocumentService().fetch_available_document_references_by_type(
            nhs_number, "ARF"
        )

        mock_dynamo.return_value.Table.assert_called_with(expected_table)

        assert len(result) == 0


def test_nothing_returned_when_invalid_doctype_supplied(nhs_number):
    expected_table = "expected_table_name"
    os.environ["LLOYD_GEORGE_DYNAMODB_NAME"] = "no-table"
    os.environ["DOCUMENT_STORE_DYNAMODB_NAME"] = expected_table

    with patch.object(boto3, "resource", return_value=MagicMock()) as mock_dynamo:
        mock_table = MagicMock()
        mock_dynamo.return_value.Table.return_value = mock_table
        result = DocumentService().fetch_available_document_references_by_type(
            nhs_number, ""
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
        MOCK_TABLE_NAME, [test_doc_ref], S3LifecycleTags.SOFT_DELETE.value
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
        MOCK_TABLE_NAME, [test_doc_ref], S3LifecycleTags.DEATH_DELETE.value
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
