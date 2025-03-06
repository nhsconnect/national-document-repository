from enum import Enum


class MultiValueEnum(Enum):
    def __new__(cls, value, *values):
        self = object.__new__(cls)
        self._value_ = value
        for v in values:
            self._add_value_alias_(v)
        return self


class DeceasedAccessReason(MultiValueEnum):
    REASON01 = "REASON01", "01"
    REASON02 = "REASON02", "02"
    REASON03 = "REASON03", "03"
    REASON04 = "REASON04", "04"
    REASON05 = "REASON05", "05"
    REASON06 = "REASON06", "06"
