from enums.metadata_field_names import DocumentReferenceMetadataFields
from utils.dynamo_utils import (
    create_expression_attribute_placeholder,
    create_expression_attribute_values,
    create_expression_value_placeholder,
    create_expressions,
    create_update_expression,
)


def test_create_expressions_correctly_creates_an_expression_of_one_field():
    expected_projection = "#VirusScannerResult_attr"
    expected_expr_attr_names = {"#VirusScannerResult_attr": "VirusScannerResult"}

    fields_requested = [DocumentReferenceMetadataFields.VIRUS_SCANNER_RESULT.value]

    actual_projection, actual_expr_attr_names = create_expressions(fields_requested)

    assert actual_projection == expected_projection
    assert actual_expr_attr_names == expected_expr_attr_names


def test_create_expressions_correctly_creates_an_expression_of_multiple_fields():
    expected_projection = "#NhsNumber_attr,#FileLocation_attr,#ContentType_attr"
    expected_expr_attr_names = {
        "#NhsNumber_attr": "NhsNumber",
        "#FileLocation_attr": "FileLocation",
        "#ContentType_attr": "ContentType",
    }

    fields_requested = [
        DocumentReferenceMetadataFields.NHS_NUMBER.value,
        DocumentReferenceMetadataFields.FILE_LOCATION.value,
        DocumentReferenceMetadataFields.CONTENT_TYPE.value,
    ]

    actual_projection, actual_expr_attr_names = create_expressions(fields_requested)

    assert actual_projection == expected_projection
    assert actual_expr_attr_names == expected_expr_attr_names


def test_create_expression_attribute_values():
    attribute_field_values = {
        DocumentReferenceMetadataFields.DELETED.value: "True",
        DocumentReferenceMetadataFields.VIRUS_SCANNER_RESULT.value: "Scanned",
    }
    expected = {":Deleted_val": "True", ":VirusScannerResult_val": "Scanned"}

    actual = create_expression_attribute_values(attribute_field_values)

    assert actual == expected


def test_create_update_expression_multiple_values():
    field_names = ["Deleted", "VirusScannerResult"]
    expected = "SET #Deleted_attr = :Deleted_val, #VirusScannerResult_attr = :VirusScannerResult_val"

    actual = create_update_expression(field_names)

    assert actual == expected


def test_create_update_expression_singular_value():
    field_names = ["Deleted"]
    expected = "SET #Deleted_attr = :Deleted_val"

    actual = create_update_expression(field_names)

    assert actual == expected


def test_create_expression_value_placeholder_capital_camel_case():
    test_value = "VirusScannerResult"
    expected = ":VirusScannerResult_val"

    actual = create_expression_value_placeholder(test_value)

    assert actual == expected


def test_create_expression_value_placeholder_camel_case():
    test_value = "virusScannerResult"
    expected = ":VirusScannerResult_val"

    actual = create_expression_value_placeholder(test_value)

    assert actual == expected


def test_create_expression_attribute_placeholder_capital_camel_case():
    test_value = "VirusScannerResult"
    expected = "#VirusScannerResult_attr"

    actual = create_expression_attribute_placeholder(test_value)

    assert actual == expected


def test_create_expression_attribute_placeholder_camel_case():
    test_value = "virusScannerResult"
    expected = "#VirusScannerResult_attr"

    actual = create_expression_attribute_placeholder(test_value)

    assert actual == expected
