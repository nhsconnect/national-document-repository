import os
from unittest.mock import MagicMock, patch

import boto3
import pytest
from models.document_reference import DocumentReference
from tests.unit.helpers.data.dynamo_responses import (
    MOCK_DOCUMENT_QUERY_RESPONSE, MOCK_EMPTY_RESPONSE)

from lambdas.services.document_service import DocumentService


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
        mock_table.query.return_value = MOCK_DOCUMENT_QUERY_RESPONSE
        result = DocumentService().retrieve_all_document_references(nhs_number, "LG")

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
        result = DocumentService().retrieve_all_document_references(nhs_number, "LG")

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
        result = DocumentService().retrieve_all_document_references(nhs_number, "ARF")

        mock_dynamo.return_value.Table.assert_called_with(expected_table)

        assert len(result) == 0


def test_nothing_returned_when_invalid_doctype_supplied(nhs_number):
    expected_table = "expected_table_name"
    os.environ["LLOYD_GEORGE_DYNAMODB_NAME"] = "no-table"
    os.environ["DOCUMENT_STORE_DYNAMODB_NAME"] = expected_table

    with patch.object(boto3, "resource", return_value=MagicMock()) as mock_dynamo:
        mock_table = MagicMock()
        mock_dynamo.return_value.Table.return_value = mock_table
        result = DocumentService().retrieve_all_document_references(nhs_number, "")

        assert len(result) == 0
