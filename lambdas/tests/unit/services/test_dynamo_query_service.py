from unittest.mock import patch, MagicMock

import boto3
import pytest
from boto3.dynamodb.conditions import Key

from enums.metadata_field_names import DynamoField
from tests.unit.helpers.dynamo_responses import MOCK_RESPONSE
from services.dynamo_query_service import DynamoQueryService


@pytest.fixture
def mock_boto3_dynamo():
    return MagicMock()


@pytest.fixture
def mock_dynamo_table():
    return MagicMock()


def test_create_expressions_correctly_creates_an_expression_of_one_field():
    query_service = DynamoQueryService("test_table")
    expected_projection = "#vscanResult"
    expected_expr_attr_names = '"#vscanResult":"VirusScanResult"'

    fields_requested = [DynamoField.VIRUS_SCAN_RESULT]

    actual_projection, actual_expr_attr_names = query_service.create_expressions(fields_requested)

    assert actual_projection == expected_projection
    assert actual_expr_attr_names == expected_expr_attr_names


def test_create_expressions_correctly_creates_an_expression_of_multiple_fields():
    query_service = DynamoQueryService("test_table")
    expected_projection = "#nhsNumber,#indexed,#type"
    expected_expr_attr_names = '"#nhsNumber":"NhsNumber","#indexed":"Indexed","#type":"Type"'

    fields_requested = [DynamoField.NHS_NUMBER, DynamoField.INDEXED, DynamoField.TYPE]

    actual_projection, actual_expr_attr_names = query_service.create_expressions(fields_requested)

    assert actual_projection == expected_projection
    assert actual_expr_attr_names == expected_expr_attr_names


def test_lambda_handler_returns_items_from_dynamo(mock_dynamo_table, mock_boto3_dynamo):
    with patch.object(boto3, "resource", return_value=mock_boto3_dynamo):
        mock_boto3_dynamo.Table.return_value = mock_dynamo_table
        mock_dynamo_table.query.return_value = MOCK_RESPONSE
        expected = MOCK_RESPONSE

        query_service = DynamoQueryService("test_table")
        actual = query_service("1234567890", [DynamoField.FILE_NAME, DynamoField.CREATED])

        search_key_obj = Key('NhsNumber').eq("1234567890")

        expected_projection = "#fileName,#created"
        expected_expr_attr_names = '"#fileName":"FileName","#created":"Created"'
        with patch.object(Key, "eq", return_value=search_key_obj):
            mock_dynamo_table.query.assert_called_with(
                IndexName='NhsNumberIndex',
                KeyConditionExpression=search_key_obj,
                ExpressionAttributeNames=expected_expr_attr_names,
                ProjectionExpression=expected_projection
            )

            assert expected == actual
