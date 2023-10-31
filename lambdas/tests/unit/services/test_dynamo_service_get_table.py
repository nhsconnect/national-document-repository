from unittest.mock import MagicMock, patch

import boto3
import pytest
from botocore.exceptions import ClientError
from services.dynamo_service import DynamoDBService
from tests.unit.conftest import MOCK_TABLE_NAME
from tests.unit.helpers.data.dynamo_responses import MOCK_SEARCH_RESPONSE


@pytest.fixture
def mock_boto3_dynamo():
    return MagicMock()


@pytest.fixture
def mock_dynamo_table():
    return MagicMock()


def test_when_table_exists_then_table_is_returned_successfully(
    set_env, mock_dynamo_table, mock_boto3_dynamo
):
    with patch.object(boto3, "resource", return_value=mock_boto3_dynamo):
        mock_boto3_dynamo.Table.return_value = mock_dynamo_table
        mock_dynamo_table.query.return_value = MOCK_SEARCH_RESPONSE

        db_service = DynamoDBService()
        actual = db_service.get_table(
            MOCK_TABLE_NAME,
        )

        assert mock_dynamo_table == actual


def test_when_table_does_not_exists_then_exception_is_raised(
    set_env, mock_dynamo_table, mock_boto3_dynamo
):
    with patch.object(boto3, "resource", return_value=mock_boto3_dynamo):
        error = {"Error": {"Code": 500, "Message": "Table not found"}}
        expected_response = ClientError(error, "Query")
        mock_boto3_dynamo.Table.return_value = expected_response

        db_service = DynamoDBService()
        actual = db_service.get_table(
            MOCK_TABLE_NAME,
        )

        assert expected_response == actual
