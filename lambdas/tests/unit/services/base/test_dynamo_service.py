import pytest
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from enums.metadata_field_names import DocumentReferenceMetadataFields
from services.base.dynamo_service import DynamoDBService
from tests.unit.conftest import MOCK_TABLE_NAME, TEST_NHS_NUMBER
from tests.unit.helpers.data.dynamo_responses import MOCK_SEARCH_RESPONSE
from utils.exceptions import DynamoServiceException


@pytest.fixture
def mock_service(set_env, mocker):
    mocker.patch("boto3.resource")
    service = DynamoDBService()
    yield service


@pytest.fixture
def mock_dynamo_service(mocker, mock_service):
    dynamo = mocker.patch.object(mock_service, "dynamodb")
    yield dynamo


@pytest.fixture
def mock_table(mocker, mock_service):
    table = mocker.patch.object(mock_service, "get_table")
    yield table


def test_query_with_requested_fields_returns_items_from_dynamo(
    mock_service, mock_table
):
    search_key_obj = Key("NhsNumber").eq(TEST_NHS_NUMBER)
    expected_projection = "#FileName_attr,#Created_attr"
    expected_expr_attr_names = {
        "#FileName_attr": "FileName",
        "#Created_attr": "Created",
    }

    mock_table.return_value.query.return_value = MOCK_SEARCH_RESPONSE
    expected = MOCK_SEARCH_RESPONSE

    actual = mock_service.query_with_requested_fields(
        MOCK_TABLE_NAME,
        "NhsNumberIndex",
        "NhsNumber",
        TEST_NHS_NUMBER,
        [
            DocumentReferenceMetadataFields.FILE_NAME.value,
            DocumentReferenceMetadataFields.CREATED.value,
        ],
    )

    mock_table.assert_called_with(MOCK_TABLE_NAME)
    mock_table.return_value.query.assert_called_once_with(
        IndexName="NhsNumberIndex",
        KeyConditionExpression=search_key_obj,
        ExpressionAttributeNames=expected_expr_attr_names,
        ProjectionExpression=expected_projection,
    )

    assert expected == actual


def test_query_with_requested_fields_with_filter_returns_items_from_dynamo(
    mock_service, mock_table
):
    search_key_obj = Key("NhsNumber").eq(TEST_NHS_NUMBER)
    expected_projection = "#FileName_attr,#Created_attr"
    expected_expr_attr_names = {
        "#FileName_attr": "FileName",
        "#Created_attr": "Created",
    }
    expected_filter = "attribute_not_exists(Deleted) OR Deleted = :Deleted_val"
    expected_attributes_values = {":Deleted_val": ""}

    mock_table.return_value.query.return_value = MOCK_SEARCH_RESPONSE
    expected = MOCK_SEARCH_RESPONSE

    actual = mock_service.query_with_requested_fields(
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

    mock_table.assert_called_with(MOCK_TABLE_NAME)
    mock_table.return_value.query.assert_called_once_with(
        IndexName="NhsNumberIndex",
        KeyConditionExpression=search_key_obj,
        ExpressionAttributeNames=expected_expr_attr_names,
        ProjectionExpression=expected_projection,
        FilterExpression=expected_filter,
        ExpressionAttributeValues=expected_attributes_values,
    )

    assert expected == actual


def test_query_with_requested_fields_raises_exception_when_results_are_empty(
    mock_service, mock_table
):
    mock_table.return_value.query.return_value = []

    with pytest.raises(DynamoServiceException):
        mock_service.query_with_requested_fields(
            MOCK_TABLE_NAME,
            "NhsNumberIndex",
            "NhsNumber",
            TEST_NHS_NUMBER,
            [
                DocumentReferenceMetadataFields.FILE_NAME.value,
                DocumentReferenceMetadataFields.CREATED.value,
            ],
        )


def test_query_with_requested_fields_raises_exception_when_fields_requested_is_empty(
    mock_service,
):
    with pytest.raises(DynamoServiceException):
        mock_service.query_with_requested_fields(
            MOCK_TABLE_NAME, "test_index", "NhsNumber", TEST_NHS_NUMBER, []
        )


def test_query_with_requested_fields_raises_exception_when_fields_requested_is_none(
    mock_service,
):
    with pytest.raises(DynamoServiceException):
        mock_service.query_with_requested_fields(
            MOCK_TABLE_NAME, "test_index", "NhsNumber", TEST_NHS_NUMBER
        )


def test_simple_query_is_called_with_correct_parameters(mock_service, mock_table):
    mock_table.return_value.query.return_value = {
        "Items": [{"id": "fake_test_item"}],
        "Counts": 1,
    }

    mock_service.simple_query(MOCK_TABLE_NAME, "test_key_condition_expression")

    mock_table.assert_called_with(MOCK_TABLE_NAME)
    mock_table.return_value.query.assert_called_once_with(
        KeyConditionExpression="test_key_condition_expression"
    )


def test_create_item_is_called_with_correct_parameters(mock_service, mock_table):
    mock_service.create_item(MOCK_TABLE_NAME, {"NhsNumber": TEST_NHS_NUMBER})

    mock_table.assert_called_with(MOCK_TABLE_NAME)
    mock_table.return_value.put_item.assert_called_once_with(
        Item={"NhsNumber": TEST_NHS_NUMBER}
    )


def test_delete_item_is_called_with_correct_parameters(mock_service, mock_table):
    mock_service.delete_item(MOCK_TABLE_NAME, {"NhsNumber": TEST_NHS_NUMBER})

    mock_table.assert_called_with(MOCK_TABLE_NAME)
    mock_table.return_value.delete_item.assert_called_once_with(
        Key={"NhsNumber": TEST_NHS_NUMBER}
    )


def test_update_item_is_called_with_correct_parameters(mock_service, mock_table):
    update_key = {"ID": "9000000009"}
    expected_update_expression = (
        "SET #FileName_attr = :FileName_val, #Deleted_attr = :Deleted_val"
    )
    expected_expr_attr_names = {
        "#FileName_attr": "FileName",
        "#Deleted_attr": "Deleted",
    }
    expected_expr_attr_values = {
        ":FileName_val": "test-filename",
        ":Deleted_val": "test-delete",
    }

    mock_service.update_item(
        MOCK_TABLE_NAME,
        TEST_NHS_NUMBER,
        {
            DocumentReferenceMetadataFields.FILE_NAME.value: "test-filename",
            DocumentReferenceMetadataFields.DELETED.value: "test-delete",
        },
    )

    mock_table.assert_called_with(MOCK_TABLE_NAME)
    mock_table.return_value.update_item.assert_called_once_with(
        Key=update_key,
        UpdateExpression=expected_update_expression,
        ExpressionAttributeNames=expected_expr_attr_names,
        ExpressionAttributeValues=expected_expr_attr_values,
    )


def test_scan_table_is_called_with_correct_no_args(mock_service, mock_table):
    mock_table.return_value.scan.return_value = []

    mock_service.scan_table(MOCK_TABLE_NAME)
    mock_table.return_value.scan.assert_called_once()


def test_scan_table_is_called_with_with_filter(mock_service, mock_table):
    mock_table.return_value.scan.return_value = []

    mock_service.scan_table(MOCK_TABLE_NAME, filter_expression="filter_test")
    mock_table.return_value.scan.assert_called_once_with(FilterExpression="filter_test")


def test_scan_table_with_is_called_with_start_key(mock_service, mock_table):
    mock_table.return_value.scan.return_value = []

    mock_service.scan_table(
        MOCK_TABLE_NAME, exclusive_start_key={"key": "exclusive_start_key"}
    )
    mock_table.return_value.scan.assert_called_once_with(
        ExclusiveStartKey={"key": "exclusive_start_key"}
    )


def test_scan_table_is_called_correctly_with_start_key_and_filter(
    mock_service, mock_table
):
    mock_table.return_value.scan.return_value = []

    mock_service.scan_table(
        MOCK_TABLE_NAME,
        exclusive_start_key={"key": "exclusive_start_key"},
        filter_expression="filter_test",
    )
    mock_table.return_value.scan.assert_called_once_with(
        ExclusiveStartKey={"key": "exclusive_start_key"},
        FilterExpression="filter_test",
    )


def test_get_table_when_table_exists_then_table_is_returned_successfully(
    mock_service, mock_dynamo_service
):
    mock_service.get_table(
        MOCK_TABLE_NAME,
    )

    mock_dynamo_service.Table.assert_called_once_with(MOCK_TABLE_NAME)


def test_get_table_when_table_does_not_exists_then_exception_is_raised(
    mock_service, mock_dynamo_service
):
    error = {"Error": {"Code": 500, "Message": "Table not found"}}
    expected_response = ClientError(error, "Query")
    mock_dynamo_service.Table.side_effect = expected_response

    with pytest.raises(ClientError):
        actual = mock_service.get_table(
            MOCK_TABLE_NAME,
        )
        assert expected_response == actual


def test_dynamo_service_singleton_instance(mocker):
    mocker.patch("boto3.resource")

    instance_1 = DynamoDBService()
    instance_2 = DynamoDBService()

    assert instance_1 is instance_2
