from unittest.mock import MagicMock, patch

import boto3
import pytest
from boto3.dynamodb.conditions import Key
from enums.metadata_field_names import DocumentReferenceMetadataFields
from services.dynamo_service import DynamoDBService
from tests.unit.conftest import MOCK_TABLE_NAME, TEST_NHS_NUMBER
from tests.unit.helpers.data.dynamo_responses import MOCK_RESPONSE
from utils.exceptions import DynamoDbException, InvalidResourceIdException


@pytest.fixture
def mock_boto3_dynamo():
    return MagicMock()


@pytest.fixture
def mock_dynamo_table():
    return MagicMock()


def test_create_expressions_correctly_creates_an_expression_of_one_field(set_env):
    query_service = DynamoDBService()
    expected_projection = "#vscanResult"
    expected_expr_attr_names = {"#vscanResult": "VirusScannerResult"}

    fields_requested = [DocumentReferenceMetadataFields.VIRUS_SCAN_RESULT]

    actual_projection, actual_expr_attr_names = query_service.create_expressions(
        fields_requested
    )

    assert actual_projection == expected_projection
    assert actual_expr_attr_names == expected_expr_attr_names


def test_create_expressions_correctly_creates_an_expression_of_multiple_fields(set_env):
    query_service = DynamoDBService()
    expected_projection = "#nhsNumber,#fileLocation,#type"
    expected_expr_attr_names = {
        "#nhsNumber": "NhsNumber",
        "#fileLocation": "FileLocation",
        "#type": "Type",
    }

    fields_requested = [
        DocumentReferenceMetadataFields.NHS_NUMBER,
        DocumentReferenceMetadataFields.FILE_LOCATION,
        DocumentReferenceMetadataFields.TYPE,
    ]

    actual_projection, actual_expr_attr_names = query_service.create_expressions(
        fields_requested
    )

    assert actual_projection == expected_projection
    assert actual_expr_attr_names == expected_expr_attr_names


def test_lambda_handler_returns_items_from_dynamo(
    set_env, mock_dynamo_table, mock_boto3_dynamo
):
    with patch.object(boto3, "resource", return_value=mock_boto3_dynamo):
        mock_boto3_dynamo.Table.return_value = mock_dynamo_table
        mock_dynamo_table.query.return_value = MOCK_RESPONSE
        expected = MOCK_RESPONSE
        search_key_obj = Key("NhsNumber").eq(TEST_NHS_NUMBER)
        expected_projection = "#fileName,#created"
        expected_expr_attr_names = {"#fileName": "FileName", "#created": "Created"}

        with patch.object(Key, "eq", return_value=search_key_obj):
            db_service = DynamoDBService()
            actual = db_service.query_service(
                MOCK_TABLE_NAME,
                "NhsNumberIndex",
                "NhsNumber",
                TEST_NHS_NUMBER,
                [
                    DocumentReferenceMetadataFields.FILE_NAME,
                    DocumentReferenceMetadataFields.CREATED,
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
        query_service = DynamoDBService()
        with pytest.raises(InvalidResourceIdException):
            query_service.query_service(
                MOCK_TABLE_NAME, "test_index", "NhsNumber", TEST_NHS_NUMBER, []
            )


def test_error_raised_when_fields_requested_is_none(
    mock_dynamo_table, mock_boto3_dynamo
):
    with patch.object(boto3, "resource", return_value=mock_boto3_dynamo):
        mock_boto3_dynamo.Table.return_value = mock_dynamo_table
        query_service = DynamoDBService()
        with pytest.raises(InvalidResourceIdException):
            query_service.query_service(
                MOCK_TABLE_NAME, "test_index", "NhsNumber", TEST_NHS_NUMBER
            )


def test_post_item_to_dynamo(mock_dynamo_table, mock_boto3_dynamo):
    with patch.object(boto3, "resource", return_value=mock_boto3_dynamo):
        mock_boto3_dynamo.Table.return_value = mock_dynamo_table
        db_service = DynamoDBService()
        db_service.post_item_service(MOCK_TABLE_NAME, {"NhsNumber": TEST_NHS_NUMBER})
        mock_dynamo_table.put_item.assert_called_once()


def test_DynamoDbException_raised_when_results_are_invalid(
    mock_dynamo_table, mock_boto3_dynamo
):
    with patch.object(boto3, "resource", return_value=mock_boto3_dynamo):
        mock_boto3_dynamo.Table.return_value = mock_dynamo_table
        mock_dynamo_table.query.return_value = []
        search_key_obj = Key("NhsNumber").eq(TEST_NHS_NUMBER)

        with patch.object(Key, "eq", return_value=search_key_obj):
            db_service = DynamoDBService()

            with pytest.raises(DynamoDbException):
                db_service.query_service(
                    MOCK_TABLE_NAME,
                    "NhsNumberIndex",
                    "NhsNumber",
                    TEST_NHS_NUMBER,
                    [
                        DocumentReferenceMetadataFields.FILE_NAME,
                        DocumentReferenceMetadataFields.CREATED,
                    ],
                )
