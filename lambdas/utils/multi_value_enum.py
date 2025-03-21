from enum import Enum


class MultiValueEnum(Enum):
    def __new__(cls, value, additional_value):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.additional_value = additional_value
        return obj

    @classmethod
    def list(cls):
        return [member.value for member in cls]
