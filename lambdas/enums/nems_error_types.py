from enum import Enum


class NEMS_ERROR_TYPES(str, Enum):
    Transient = "transient"
    Data = "data"
    Validation = "validation"
