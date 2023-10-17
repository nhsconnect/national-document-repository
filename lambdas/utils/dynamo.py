import inflection


def create_expressions(requested_fields: list) -> tuple[str, dict]:
    """
    Creates expression components for a dynamo query
        :param requested_fields: List of enum fields names

    example usage:
        requested_fields = [enum.ID, enum.CREATED", "enum.FILE_NAME"]
        projection_expression, expression_attribute_names = create_expressions(requested_fields)

    result:
        [
            "#id,#created,#fileName",
            {"#id": "Id", "#created": "Created", "#fileName": "FileName"}
        ]
    """
    projection_expression = ""
    expression_attribute_names = {}

    for field_definition in requested_fields:
        if len(projection_expression) > 0:
            projection_expression = (
                f"{projection_expression},{field_definition.field_alias}"
            )
        else:
            projection_expression = field_definition.field_alias

        expression_attribute_names[field_definition.field_alias] = str(
            field_definition.field_name
        )

    return projection_expression, expression_attribute_names


def create_nonexistant_or_empty_attr_filter(field_names: list):
    """
    Creates a filter for dynamodb queries in which an attribute may not yet exist for an item
        :param field_names: List of fields which may not yet exist in the table

    example usage:
        field_names = ["Name", "Age"...]
        fields_filter = create_nonexistant_or_empty_attr_filter(field_names)

    result:
        "attribute_not_exists(Name) OR Name = :name_value"

    """
    attr_filter = ""
    for field in field_names:
        filter_string = f"attribute_not_exists({field}) OR {field} = {create_expression_placeholder(field)}"
        if not attr_filter:
            attr_filter = filter_string
        else:
            attr_filter += f" AND {filter_string}"

    return attr_filter


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
            ":deleted_value" : ""
            ":virus_scan_result_value" : "Scanned"
        }
    """
    expression_attribute_values = {}
    for name, value in zip(expression_names, expression_values):
        expression_attribute_values[f"{create_expression_placeholder(name)}"] = value

    return expression_attribute_values


def create_expression_placeholder(value: str) -> str:
    """
    Creates a placeholder value for an expression attribute name
        :param value: Value to change into a placeholder

    example usage:
        placeholder = create_expression_placeholder("VirusScanResult")

    result:
        ":virus_scan_result_value"
    """
    return f":{inflection.underscore(value)}_value"
