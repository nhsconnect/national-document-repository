from boto3.dynamodb.conditions import Attr, ConditionBase
from enums.dynamo_filter import AttributeOperator, ConditionOperator
from utils.exceptions import DynamoServiceException


class DynamoQueryFilterBuilder:
    def __init__(self):
        self.filter_conditions: list[Attr] = []
        self.conditions_operator: ConditionOperator = ConditionOperator.AND

    def add_condition(
        self, attribute: str, attr_operator: AttributeOperator, filter_value=None
    ):
        """
        Args:
            attribute: The DynamoDb table field name we want to apply a condition on
            attr_operator: DynamoDb operator we want to apply to the query (e.g. eq, gt, lt)
            filter_value: The value of our filter

        Returns:
            Return instance of self, with a populated list of filter conditions

        Example Usage:
            filter_builder = DynamoQueryFilterBuilder()
            filter_builder.add_condition(
                attribute="Name",
                attr_operator=AttributeOperator.EQUAL,
                filter_value="John",
            )
            .add_condition(
                attribute="Age",
                attr_operator=AttributeOperator.LESS_THAN,
                filter_value=80
            )
            .build()
        """

        try:
            if filter_value:
                condition = getattr(Attr(attribute), attr_operator.value)(filter_value)
            else:
                condition = getattr(Attr(attribute), attr_operator.value)()
        except AttributeError:
            raise DynamoServiceException(
                f"Unsupported attribute filter operator: {attr_operator}"
            )
        self.filter_conditions.append(condition)
        return self

    def set_combination_operator(self, operator: ConditionOperator):
        """
        Args:
            operator: Change the operator of the filter combinations.
                The default is AND e.g. filter by condition1 AND condition2

        Returns:
            Return instance of self, with an updated filter combination operator

        Example Usage:
            filter_builder = DynamoQueryFilterBuilder()
            filter_builder.add_condition(
                attribute="Name",
                attr_operator=AttributeOperator.EQUAL,
                filter_value="John",
            )
            .add_condition(
                attribute="Name",
                attr_operator=AttributeOperator.EQUAL,
                filter_value="Steve",
            )
            .set_combination_operator(operator=ConditionOperator.OR)
            .build()
        """
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
