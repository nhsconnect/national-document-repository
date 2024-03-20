import inflection
from boto3.dynamodb.conditions import Attr, ConditionBase
from enums.dynamo_filter import AttributeOperator, ConditionOperator


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


def create_update_expression(field_names: list) -> str:
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
        expression = f" {create_expression_attribute_placeholder(field)} = {create_expression_value_placeholder(field)}"
        if update_expression == "SET":
            update_expression += expression
        else:
            update_expression += f",{expression}"

    return update_expression


def create_expression_attribute_values(attribute_field_values: dict) -> dict:
    """
    Maps a dict of expression names and expression values to create a dictionary to pass into query
        :param attribute_field_values: Dictionary of attribute field names and values

    example usage:
        attribute_field_values = {
                DocumentReferenceMetadataFields.DELETED.value: "",
                DocumentReferenceMetadataFields.FILENAME.value: "Test Filename"
            }
        expression_attribute_values = create_expression_attribute_values(attribute_field_values)

    result:
        {
            ":Deleted_val" : ""
            ":FileName_val" : "Test Filename"
        }
    """
    expression_attribute_values = {}
    for field_name, field_value in attribute_field_values.items():
        expression_attribute_values[
            f"{create_expression_value_placeholder(field_name)}"
        ] = field_value

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


class DynamoQueryFilterBuilder:
    def __init__(self):
        self.filter_conditions: list[Attr] = []
        self.conditions_operator: ConditionOperator = ConditionOperator.AND

    def add_condition(
        self, attribute: str, attr_operator: AttributeOperator, filter_value
    ):
        match attr_operator:
            case AttributeOperator.EQUAL:
                condition = Attr(attribute).eq(filter_value)
            case AttributeOperator.NOT_EQUAL:
                condition = Attr(attribute).ne(filter_value)
            case AttributeOperator.GREATER_THAN:
                condition = Attr(attribute).gt(filter_value)
            case AttributeOperator.GREATER_OR_EQUAL:
                condition = Attr(attribute).gte(filter_value)
            case AttributeOperator.LESS_THAN:
                condition = Attr(attribute).lt(filter_value)
            case AttributeOperator.LESS_THAN_OR_EQUAL:
                condition = Attr(attribute).lte(filter_value)
            case _:
                raise ValueError(f"Unsupported attribute operator: {attr_operator}")

        self.filter_conditions.append(condition)
        return self

    def set_combination_operator(self, operator: ConditionOperator):
        self.conditions_operator = operator
        return self

    def build(self) -> Attr | ConditionBase:
        if not self.filter_conditions:
            return None

        combined_condition = self.filter_conditions[0]
        for condition in self.filter_conditions[1:]:
            if self.conditions_operator == ConditionOperator.AND:
                combined_condition &= condition
            elif self.conditions_operator == ConditionOperator.OR:
                combined_condition |= condition

        self.filter_conditions = []
        return combined_condition
