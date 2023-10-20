from enum import Enum


class S3LifecycleTags(Enum):
    SOFT_DELETE_KEY = "soft-delete"
    SOFT_DELETE_VAL = "true"
    SOFT_DELETE_DAYS = 56
    DEATH_DELETE_KEY = "patient-death"
    DEATH_DELETE_VAL = "true"
    DEATH_DELETE_DAYS = 3650
