from unittest.mock import MagicMock, patch

import boto3
import pytest
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from enums.metadata_field_names import DocumentReferenceMetadataFields
from services.dynamo_service import DynamoDBService
from tests.unit.conftest import MOCK_TABLE_NAME, TEST_NHS_NUMBER
from tests.unit.helpers.data.dynamo_responses import MOCK_SEARCH_RESPONSE
from utils.exceptions import DynamoDbException, InvalidResourceIdException


@pytest.fixture
def mock_boto3_dynamo():
    return MagicMock()


@pytest.fixture
def mock_dynamo_table():
    return MagicMock()


def test_lambda_handler_returns_items_from_dynamo(
    set_env, mock_dynamo_table, mock_boto3_dynamo
):
    with patch.object(boto3, "resource", return_value=mock_boto3_dynamo):
        mock_boto3_dynamo.Table.return_value = mock_dynamo_table
        mock_dynamo_table.query.return_value = MOCK_SEARCH_RESPONSE
        expected = MOCK_SEARCH_RESPONSE
        search_key_obj = Key("NhsNumber").eq(TEST_NHS_NUMBER)
        expected_projection = "#FileName_attr,#Created_attr"
        expected_expr_attr_names = {
            "#FileName_attr": "FileName",
            "#Created_attr": "Created",
        }

        with patch.object(Key, "eq", return_value=search_key_obj):
            db_service = DynamoDBService()
            actual = db_service.query_with_requested_fields(
                MOCK_TABLE_NAME,
                "NhsNumberIndex",
                "NhsNumber",
                TEST_NHS_NUMBER,
                [
                    DocumentReferenceMetadataFields.FILE_NAME.value,
                    DocumentReferenceMetadataFields.CREATED.value,
                ],
            )

            mock_dynamo_table.query.assert_called_with(
                IndexName="NhsNumberIndex",
                KeyConditionExpression=search_key_obj,
                ExpressionAttributeNames=expected_expr_attr_names,
                ProjectionExpression=expected_projection,
            )

            assert expected == actual


def test_lambda_handler_returns_items_from_dynamo_with_filter(
    set_env, mock_dynamo_table, mock_boto3_dynamo
):
    with patch.object(boto3, "resource", return_value=mock_boto3_dynamo):
        mock_boto3_dynamo.Table.return_value = mock_dynamo_table
        mock_dynamo_table.query.return_value = MOCK_SEARCH_RESPONSE
        expected = MOCK_SEARCH_RESPONSE
        search_key_obj = Key("NhsNumber").eq(TEST_NHS_NUMBER)
        expected_projection = "#FileName_attr,#Created_attr"
        expected_expr_attr_names = {
            "#FileName_attr": "FileName",
            "#Created_attr": "Created",
        }
        expected_filter = "attribute_not_exists(Deleted) OR Deleted = :Deleted_val"
        expected_attributes_values = {":Deleted_val": ""}

        with patch.object(Key, "eq", return_value=search_key_obj):
            db_service = DynamoDBService()
            actual = db_service.query_with_requested_fields(
                MOCK_TABLE_NAME,
                "NhsNumberIndex",
                "NhsNumber",
                TEST_NHS_NUMBER,
                [
                    DocumentReferenceMetadataFields.FILE_NAME.value,
                    DocumentReferenceMetadataFields.CREATED.value,
                ],
                filtered_fields={DocumentReferenceMetadataFields.DELETED.value: ""},
            )

            mock_dynamo_table.query.assert_called_with(
                IndexName="NhsNumberIndex",
                KeyConditionExpression=search_key_obj,
                ExpressionAttributeNames=expected_expr_attr_names,
                ProjectionExpression=expected_projection,
                FilterExpression=expected_filter,
                ExpressionAttributeValues=expected_attributes_values,
            )

            assert expected == actual


def test_error_raised_when_no_fields_requested(mock_dynamo_table, mock_boto3_dynamo):
    with patch.object(boto3, "resource", return_value=mock_boto3_dynamo):
        mock_boto3_dynamo.Table.return_value = mock_dynamo_table
        query_service = DynamoDBService()
        with pytest.raises(InvalidResourceIdException):
            query_service.query_with_requested_fields(
                MOCK_TABLE_NAME, "test_index", "NhsNumber", TEST_NHS_NUMBER, []
            )


def test_error_raised_when_fields_requested_is_none(
    mock_dynamo_table, mock_boto3_dynamo
):
    with patch.object(boto3, "resource", return_value=mock_boto3_dynamo):
        mock_boto3_dynamo.Table.return_value = mock_dynamo_table
        query_service = DynamoDBService()
        with pytest.raises(InvalidResourceIdException):
            query_service.query_with_requested_fields(
                MOCK_TABLE_NAME, "test_index", "NhsNumber", TEST_NHS_NUMBER
            )


def test_post_item_to_dynamo(mock_dynamo_table, mock_boto3_dynamo):
    with patch.object(boto3, "resource", return_value=mock_boto3_dynamo):
        mock_boto3_dynamo.Table.return_value = mock_dynamo_table
        db_service = DynamoDBService()
        db_service.create_item(MOCK_TABLE_NAME, {"NhsNumber": TEST_NHS_NUMBER})
        mock_dynamo_table.put_item.assert_called_once()


def test_simple_query(mock_dynamo_table, mock_boto3_dynamo):
    with patch.object(boto3, "resource", return_value=mock_boto3_dynamo):
        mock_boto3_dynamo.Table.return_value = mock_dynamo_table
        mock_dynamo_table.query.return_value = {
            "Items": [{"id": "fake_test_item"}],
            "Counts": 1,
        }

        db_service = DynamoDBService()
        db_service.simple_query("test_table", "test_key_condition_expression")

        mock_boto3_dynamo.Table.assert_called_with("test_table")
        mock_dynamo_table.query.assert_called_with(
            KeyConditionExpression="test_key_condition_expression"
        )


def test_delete_item(mock_dynamo_table, mock_boto3_dynamo):
    with patch.object(boto3, "resource", return_value=mock_boto3_dynamo):
        mock_boto3_dynamo.Table.return_value = mock_dynamo_table

        db_service = DynamoDBService()
        db_service.delete_item("test_table", {"NhsNumber": "0123456789"})

        mock_boto3_dynamo.Table.assert_called_with("test_table")
        mock_dynamo_table.delete_item.assert_called_with(
            Key={"NhsNumber": "0123456789"}
        )


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
                db_service.query_with_requested_fields(
                    MOCK_TABLE_NAME,
                    "NhsNumberIndex",
                    "NhsNumber",
                    TEST_NHS_NUMBER,
                    [
                        DocumentReferenceMetadataFields.FILE_NAME.value,
                        DocumentReferenceMetadataFields.CREATED.value,
                    ],
                )


def test_test_scan_table_no_args(mock_dynamo_table, mock_boto3_dynamo):
    with patch.object(boto3, "resource", return_value=mock_boto3_dynamo):
        mock_boto3_dynamo.Table.return_value = mock_dynamo_table
        mock_dynamo_table.scan.return_value = []

        db_service = DynamoDBService()
        db_service.scan_table(MOCK_TABLE_NAME)
        mock_dynamo_table.scan.assert_called_once()


def test_test_scan_table_with_filter(mock_dynamo_table, mock_boto3_dynamo):
    with patch.object(boto3, "resource", return_value=mock_boto3_dynamo):
        mock_boto3_dynamo.Table.return_value = mock_dynamo_table
        mock_dynamo_table.scan.return_value = []

        db_service = DynamoDBService()
        db_service.scan_table(MOCK_TABLE_NAME, filter_expression="filter_test")
        mock_dynamo_table.scan.assert_called_with(FilterExpression="filter_test")


def test_test_scan_table_with_start_key(mock_dynamo_table, mock_boto3_dynamo):
    with patch.object(boto3, "resource", return_value=mock_boto3_dynamo):
        mock_boto3_dynamo.Table.return_value = mock_dynamo_table
        mock_dynamo_table.scan.return_value = []

        db_service = DynamoDBService()
        db_service.scan_table(
            MOCK_TABLE_NAME, exclusive_start_key={"key": "exclusive_start_key"}
        )
        mock_dynamo_table.scan.assert_called_with(
            ExclusiveStartKey={"key": "exclusive_start_key"}
        )


def test_test_scan_table_with_start_key_and_filter(
    mock_dynamo_table, mock_boto3_dynamo
):
    with patch.object(boto3, "resource", return_value=mock_boto3_dynamo):
        mock_boto3_dynamo.Table.return_value = mock_dynamo_table
        mock_dynamo_table.scan.return_value = []

        db_service = DynamoDBService()
        db_service.scan_table(
            MOCK_TABLE_NAME,
            exclusive_start_key={"key": "exclusive_start_key"},
            filter_expression="filter_test",
        )
        mock_dynamo_table.scan.assert_called_with(
            ExclusiveStartKey={"key": "exclusive_start_key"},
            FilterExpression="filter_test",
        )


def test_batch_write_to_dynamo(mock_dynamo_table, mock_boto3_dynamo, mocker):
    with patch.object(boto3, "resource", return_value=mock_boto3_dynamo):
        db_service = DynamoDBService()
        mock_batch_writer = mocker.MagicMock()
        mock_dynamo_table.batch_writer.return_value = mock_batch_writer
        mock_batch_writer.__enter__ = mocker.MagicMock(return_value=mock_batch_writer)
        mock_batch_writer.__exit__ = mocker.MagicMock(return_value=None)
        mock_boto3_dynamo.Table.return_value = mock_dynamo_table
        items = [{"NhsNumber": TEST_NHS_NUMBER}, {"NhsNumber": "12435255"}]

        db_service.batch_writing(MOCK_TABLE_NAME, items)

        mock_batch_writer.put_item.assert_has_calls(
            [mocker.call(Item=item) for item in items]
        )
        assert mock_batch_writer.put_item.call_count == 2


def test_batch_write_to_dynamo_raise_error(
    mock_dynamo_table, mock_boto3_dynamo, mocker
):
    with patch.object(boto3, "resource", return_value=mock_boto3_dynamo):
        db_service = DynamoDBService()
        mock_batch_writer = mocker.MagicMock()
        mock_dynamo_table.batch_writer.return_value = mock_batch_writer
        mock_batch_writer.__enter__ = mocker.MagicMock(return_value=mock_batch_writer)
        mock_batch_writer.__exit__ = mocker.MagicMock(return_value=None)
        mock_batch_writer.put_item.side_effect = (
            ClientError({"error": "test error message"}, "test"),
        )
        mock_boto3_dynamo.Table.return_value = mock_dynamo_table
        items = [{"NhsNumber": TEST_NHS_NUMBER}, {"NhsNumber": "12435255"}]
        with pytest.raises(ClientError):
            db_service.batch_writing(MOCK_TABLE_NAME, items)

        assert mock_batch_writer.put_item.call_count == 1
