import logging

import inflection

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def create_expressions(requested_fields: list) -> tuple[str, dict]:
    """
    Creates expression components for a dynamo query
        :param requested_fields: List of enum fields names

    example usage:
        requested_fields = ["ID", "Created", "FileName"]
        projection_expression, expression_attribute_names = create_expressions(requested_fields)

    result:
        [
            "#ID_attr,#Created_attr,#FileName_attr",
            {"#ID_attr": "ID", "#Created_attr": "Created", "#FileName_attr": "FileName"}
        ]
    """
    projection_expression = ""
    expression_attribute_names = {}

    for field_definition in requested_fields:
        field_placeholder = create_expression_attribute_placeholder(field_definition)
        if len(projection_expression) > 0:
            projection_expression = f"{projection_expression},{field_placeholder}"
        else:
            projection_expression = field_placeholder

        expression_attribute_names[field_placeholder] = field_definition
    return projection_expression, expression_attribute_names


def create_nonexistant_or_empty_attr_filter(field_names: list):
    """
    Creates a filter for dynamodb queries in which an attribute may not yet exist for an item
        :param field_names: List of fields which may not yet exist in the table

    example usage:
        field_names = ["Name", "Age"...]
        fields_filter = create_nonexistant_or_empty_attr_filter(field_names)

    result:
        "attribute_not_exists(Name) OR Name = :Name_val"

    """
    attr_filter = ""
    for field in field_names:
        filter_string = f"attribute_not_exists({field}) OR {field} = {create_expression_value_placeholder(field)}"
        if not attr_filter:
            attr_filter = filter_string
        else:
            attr_filter += f" AND {filter_string}"

    return attr_filter


def create_update_expression(field_names: list):
    """
    Creates an expression for dynamodb queries to SET a new value for an item
        :param field_names: List of fields to update

    example usage:
        field_names = ["Name", "Age"...]
        fields_filter = create_update_expression(field_names)

    result:
        "SET #Name_attr = :Name_val, #Age_attr = :Age_val"

    """
    update_expression = "SET"
    for field in field_names:
        expression = f"{create_expression_attribute_placeholder(field)} = {create_expression_value_placeholder(field)}"
        if update_expression == "SET":
            update_expression += expression
        else:
            update_expression += f", {expression}"

    return update_expression


def create_expression_attribute_values(
    expression_names: list[str], expression_values: list[str]
):
    """
    Maps a list of expression names and expression values to create a dictionary to pass into query
        :param expression_names: List of expression names
        :param expression_values: List of expression values

    example usage:
        field_names = ["Deleted", "VirusScanResult"...]
        field_values = ["", "Scanned"]
        expression_attribute_values = create_expression_attribute_values(field_names)

    result:
        {
            ":Deleted_val" : ""
            ":VirusScannerResult_val" : "Scanned"
        }
    """
    expression_attribute_values = {}
    for name, value in zip(expression_names, expression_values):
        expression_attribute_values[
            f"{create_expression_value_placeholder(name)}"
        ] = value

    return expression_attribute_values


def create_expression_value_placeholder(value: str) -> str:
    """
    Creates a placeholder value for an expression attribute name
        :param value: Value to change into a placeholder

    example usage:
        placeholder = create_expression_value_placeholder("VirusScanResult")

    result:
        ":VirusScanResult_val"
    """
    return f":{inflection.camelize(value, uppercase_first_letter=True)}_val"


def create_expression_attribute_placeholder(value: str) -> str:
    """
    Creates a placeholder value for a projection attribute name
        :param value: Value to change into a placeholder

    example usage:
        placeholder = create_expression_attribute_placeholder("VirusScanResult")

    result:
        "#VirusScanResult_attr"
    """
    return f"#{inflection.camelize(value, uppercase_first_letter=True)}_attr"
