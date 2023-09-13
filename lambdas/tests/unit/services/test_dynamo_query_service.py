from unittest.mock import MagicMock, patch

import boto3
import pytest
from boto3.dynamodb.conditions import Key
from enums.metadata_field_names import DynamoDocumentMetadataTableFields
from services.dynamo_services import DynamoDBService
from tests.unit.helpers.data.dynamo_responses import (MOCK_RESPONSE,
                                                      UNEXPECTED_RESPONSE)
from utils.exceptions import DynamoDbException, InvalidResourceIdException


@pytest.fixture
def mock_boto3_dynamo():
    return MagicMock()


@pytest.fixture
def mock_dynamo_table():
    return MagicMock()


def test_create_expressions_correctly_creates_an_expression_of_one_field():
    query_service = DynamoDBService("test_table")
    expected_projection = "#vscanResult"
    expected_expr_attr_names = {"#vscanResult": "VirusScannerResult"}

    fields_requested = [DynamoDocumentMetadataTableFields.VIRUS_SCAN_RESULT]

    actual_projection, actual_expr_attr_names = query_service.create_expressions(
        fields_requested
    )

    assert actual_projection == expected_projection
    assert actual_expr_attr_names == expected_expr_attr_names


def test_create_expressions_correctly_creates_an_expression_of_multiple_fields():
    query_service = DynamoDBService("test_table")
    expected_projection = "#nhsNumber,#indexed,#type"
    expected_expr_attr_names = {
        "#nhsNumber": "NhsNumber",
        "#indexed": "Indexed",
        "#type": "Type",
    }

    fields_requested = [
        DynamoDocumentMetadataTableFields.NHS_NUMBER,
        DynamoDocumentMetadataTableFields.INDEXED,
        DynamoDocumentMetadataTableFields.TYPE,
    ]

    actual_projection, actual_expr_attr_names = query_service.create_expressions(
        fields_requested
    )

    assert actual_projection == expected_projection
    assert actual_expr_attr_names == expected_expr_attr_names


def test_lambda_handler_returns_items_from_dynamo(mock_dynamo_table, mock_boto3_dynamo):
    with patch.object(boto3, "resource", return_value=mock_boto3_dynamo):
        mock_boto3_dynamo.Table.return_value = mock_dynamo_table
        mock_dynamo_table.query.return_value = MOCK_RESPONSE
        expected = MOCK_RESPONSE
        search_key_obj = Key("NhsNumber").eq("1234567890")
        expected_projection = "#fileName,#created"
        expected_expr_attr_names = {"#fileName": "FileName", "#created": "Created"}

        with patch.object(Key, "eq", return_value=search_key_obj):
            db_service = DynamoDBService("test_table",)
            actual = db_service.query_service(
                "NhsNumberIndex",
                "NhsNumber",
                "0123456789",
                [
                    DynamoDocumentMetadataTableFields.FILE_NAME,
                    DynamoDocumentMetadataTableFields.CREATED,
                ],
            )

            mock_dynamo_table.query.assert_called_with(
                IndexName="NhsNumberIndex",
                KeyConditionExpression=search_key_obj,
                ExpressionAttributeNames=expected_expr_attr_names,
                ProjectionExpression=expected_projection,
            )

            assert expected == actual


def test_error_raised_when_no_fields_requested(mock_dynamo_table, mock_boto3_dynamo):
    with patch.object(boto3, "resource", return_value=mock_boto3_dynamo):
        mock_boto3_dynamo.Table.return_value = mock_dynamo_table
        query_service = DynamoDBService("test_table", )
        with pytest.raises(InvalidResourceIdException):
            query_service.query_service("test_index", "NhsNumber", "0123456789", [])


def test_error_raised_when_fields_requested_is_none(
    mock_dynamo_table, mock_boto3_dynamo
):
    with patch.object(boto3, "resource", return_value=mock_boto3_dynamo):
        mock_boto3_dynamo.Table.return_value = mock_dynamo_table
        query_service = DynamoDBService("test_table")
        with pytest.raises(InvalidResourceIdException):
            query_service.query_service("test_index", "NhsNumber", "0123456789")

def test_post_item_to_dynamo(mock_dynamo_table, mock_boto3_dynamo):
    with patch.object(boto3, "resource", return_value=mock_boto3_dynamo):
        mock_boto3_dynamo.Table.return_value = mock_dynamo_table
        db_service = DynamoDBService("test_table")
        db_service.post_item_service({"NhsNumber": "0123456789"})
        mock_dynamo_table.put_item.assert_called_once()


def test_DynamoDbException_raised_when_results_are_invalid(
    mock_dynamo_table, mock_boto3_dynamo
):
    with pytest.raises(DynamoDbException):
        with patch.object(boto3, "resource", return_value=mock_boto3_dynamo):
            mock_boto3_dynamo.Table.return_value = mock_dynamo_table
            mock_dynamo_table.query.return_value = UNEXPECTED_RESPONSE
            search_key_obj = Key("NhsNumber").eq("1234567890")

            with patch.object(Key, "eq", return_value=search_key_obj):
                query_service = DynamoDBService("test_table", "NhsNumberIndex")
                query_service.query_service(
                    "NhsNumber",
                    "0123456789",
                    [
                        DynamoDocumentMetadataTableFields.FILE_NAME,
                        DynamoDocumentMetadataTableFields.CREATED,
                    ],
                )
