import pytest
from boto3.dynamodb.conditions import Attr
from enums.dynamo_filter import AttributeOperator, ConditionOperator
from enums.metadata_field_names import DocumentReferenceMetadataFields
from utils.dynamo_query_filter_builder import DynamoQueryFilterBuilder


@pytest.fixture
def dynamo_filter():
    return DynamoQueryFilterBuilder()


def test_create_query_filter_builder_handles_single_equals_attribute_filter(
    dynamo_filter,
):
    expected = Attr("Deleted").eq("Test")

    actual = dynamo_filter.add_condition(
        attribute=str(DocumentReferenceMetadataFields.DELETED.value),
        attr_operator=AttributeOperator.EQUAL,
        filter_value="Test",
    ).build()

    assert actual == expected


def test_create_query_filter_builder_handles_single_not_equals_attribute_filter(
    dynamo_filter,
):
    expected = Attr("Deleted").ne("Test")

    actual = dynamo_filter.add_condition(
        attribute=str(DocumentReferenceMetadataFields.DELETED.value),
        attr_operator=AttributeOperator.NOT_EQUAL,
        filter_value="Test",
    ).build()

    assert actual == expected


def test_create_query_filter_builder_handles_single_less_than_attribute_filter(
    dynamo_filter,
):
    expected = Attr("Deleted").lt("Test")

    actual = dynamo_filter.add_condition(
        attribute=str(DocumentReferenceMetadataFields.DELETED.value),
        attr_operator=AttributeOperator.LESS_THAN,
        filter_value="Test",
    ).build()

    assert actual == expected


def test_create_query_filter_builder_handles_single_less_than_equal_to_attribute_filter(
    dynamo_filter,
):
    expected = Attr("Deleted").lte("Test")

    actual = dynamo_filter.add_condition(
        attribute=str(DocumentReferenceMetadataFields.DELETED.value),
        attr_operator=AttributeOperator.LESS_THAN_OR_EQUAL,
        filter_value="Test",
    ).build()

    assert actual == expected


def test_create_query_filter_builder_handles_single_greater_than_attribute_filter(
    dynamo_filter,
):
    expected = Attr("Deleted").gt("Test")

    actual = dynamo_filter.add_condition(
        attribute=str(DocumentReferenceMetadataFields.DELETED.value),
        attr_operator=AttributeOperator.GREATER_THAN,
        filter_value="Test",
    ).build()

    assert actual == expected


def test_create_query_filter_builder_handles_single_greater_than_equal_to_attribute_filter(
    dynamo_filter,
):
    expected = Attr("Deleted").gte("Test")

    actual = dynamo_filter.add_condition(
        attribute=str(DocumentReferenceMetadataFields.DELETED.value),
        attr_operator=AttributeOperator.GREATER_OR_EQUAL,
        filter_value="Test",
    ).build()

    assert actual == expected


def test_create_query_filter_builder_handles_multiple_attributes_with_and_operator(
    dynamo_filter,
):
    expected = Attr("Deleted").eq("Test") & Attr("FileName").eq("Test")

    actual = (
        dynamo_filter.add_condition(
            attribute=str(DocumentReferenceMetadataFields.DELETED.value),
            attr_operator=AttributeOperator.EQUAL,
            filter_value="Test",
        )
        .add_condition(
            attribute=DocumentReferenceMetadataFields.FILE_NAME.value,
            attr_operator=AttributeOperator.EQUAL,
            filter_value="Test",
        )
        .build()
    )

    assert actual == expected


def test_create_query_filter_builder_handles_multiple_attributes_with_or_operator(
    dynamo_filter,
):
    expected = Attr("Deleted").eq("Test") | Attr("FileName").eq("Test")

    actual = (
        dynamo_filter.add_condition(
            attribute=str(DocumentReferenceMetadataFields.DELETED.value),
            attr_operator=AttributeOperator.EQUAL,
            filter_value="Test",
        )
        .add_condition(
            attribute=DocumentReferenceMetadataFields.FILE_NAME.value,
            attr_operator=AttributeOperator.EQUAL,
            filter_value="Test",
        )
        .set_combination_operator(operator=ConditionOperator.OR)
        .build()
    )

    assert actual == expected
