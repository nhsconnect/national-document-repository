from enum import Enum, IntEnum


class S3LifecycleTags(Enum):
    SOFT_DELETE = "soft-delete"
    SOFT_DELETE_VAL = "true"
    DEATH_DELETE = "patient-death"
    DEATH_DELETE_VAL = "true"


class S3LifecycleDays(IntEnum):
    SOFT_DELETE = 56
    DEATH_DELETE = 3650
