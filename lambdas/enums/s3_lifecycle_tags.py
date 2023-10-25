from enum import Enum, IntEnum


class S3LifecycleTags(Enum):
    SOFT_DELETE = "soft-delete"
    DEATH_DELETE = "patient-death"
    ENABLE_TAG = "true"


class S3LifecycleDays(IntEnum):
    SOFT_DELETE = 56
    DEATH_DELETE = 3650
