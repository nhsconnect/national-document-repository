from enums.metadata_field_names import DocumentReferenceMetadataFields
from utils.dynamo import (create_expression_attribute_values,
                          create_expression_placeholder, create_expressions,
                          create_nonexistant_or_empty_attr_filter)


def test_create_expressions_correctly_creates_an_expression_of_one_field(set_env):
    expected_projection = "#vscanResult"
    expected_expr_attr_names = {"#vscanResult": "VirusScannerResult"}

    fields_requested = [DocumentReferenceMetadataFields.VIRUS_SCAN_RESULT]

    actual_projection, actual_expr_attr_names = create_expressions(fields_requested)

    assert actual_projection == expected_projection
    assert actual_expr_attr_names == expected_expr_attr_names


def test_create_expressions_correctly_creates_an_expression_of_multiple_fields(set_env):
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

    actual_projection, actual_expr_attr_names = create_expressions(fields_requested)

    assert actual_projection == expected_projection
    assert actual_expr_attr_names == expected_expr_attr_names


def test_create_expression_attribute_values():
    field_names = ["Deleted", "VirusScannerResult"]
    field_values = ["", "Scanned"]
    expected = {":deleted_value": "", ":virus_scanner_result_value": "Scanned"}

    actual = create_expression_attribute_values(field_names, field_values)

    assert actual == expected


def test_create_nonexistant_or_empty_attr_filter_multiple_values():
    field_names = ["Deleted", "VirusScannerResult"]
    expected = (
        "attribute_not_exists(Deleted) OR Deleted = :deleted_value AND attribute_not_exists("
        "VirusScannerResult) OR VirusScannerResult = :virus_scanner_result_value"
    )

    actual = create_nonexistant_or_empty_attr_filter(field_names)

    assert actual == expected


def test_create_nonexistant_or_empty_attr_filter_singular_value():
    field_names = ["Deleted"]
    expected = "attribute_not_exists(Deleted) OR Deleted = :deleted_value"

    actual = create_nonexistant_or_empty_attr_filter(field_names)

    assert actual == expected


def test_create_expression_placeholder_capital_camel_case():
    test_value = "VirusScannerResult"
    expected = ":virus_scanner_result_value"

    actual = create_expression_placeholder(test_value)

    assert actual == expected


def test_create_expression_placeholder_camel_case():
    test_value = "virusScannerResult"
    expected = ":virus_scanner_result_value"

    actual = create_expression_placeholder(test_value)

    assert actual == expected
