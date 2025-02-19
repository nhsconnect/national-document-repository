from boto3.dynamodb.conditions import Attr, ConditionBase
from enums.dynamo_filter import AttributeOperator, ConditionOperator
from utils.exceptions import DynamoServiceException


class DynamoQueryFilterBuilder:
    def __init__(self):
        self.filter_conditions: list[Attr] = []
        self.conditions_operator: ConditionOperator = ConditionOperator.AND

    def add_condition(
        self, attribute: str, attr_operator: AttributeOperator, filter_value
    ):
        try:
            condition = getattr(Attr(attribute), attr_operator.value)(filter_value)
        except AttributeError:
            raise DynamoServiceException(
                f"Unsupported attribute filter operator: {attr_operator}"
            )
        self.filter_conditions.append(condition)
        return self

    def set_combination_operator(self, operator: ConditionOperator):
        self.conditions_operator = operator
        return self

    def build(self) -> Attr | ConditionBase:
        if not self.filter_conditions:
            raise DynamoServiceException("Unable to build empty attribute filter")

        combined_condition = self.filter_conditions[0]
        for condition in self.filter_conditions[1:]:
            if self.conditions_operator == ConditionOperator.AND:
                combined_condition &= condition
            elif self.conditions_operator == ConditionOperator.OR:
                combined_condition |= condition

        self.filter_conditions = []
        return combined_condition
