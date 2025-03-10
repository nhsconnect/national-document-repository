from enum import Enum


class MultiValueEnum(Enum):
    def __new__(cls, value, *values):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.additional_values = values
        return obj

    @classmethod
    def list(cls):
        return [member.value for member in cls]


class DeceasedAccessReason(MultiValueEnum):
    REASON01 = "01", "REASON01"
    REASON02 = "02", "REASON02"
    REASON03 = "03", "REASON03"
    REASON04 = "04", "REASON04"
    REASON05 = "05", "REASON05"
    REASON06 = "06", "REASON06"
