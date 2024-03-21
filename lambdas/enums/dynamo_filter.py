from enum import Enum


class AttributeOperator(Enum):
    EQUAL = "eq"
    NOT_EQUAL = "ne"
    GREATER_THAN = "gt"
    GREATER_OR_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"


class ConditionOperator(Enum):
    OR = "|"
    AND = "&"
