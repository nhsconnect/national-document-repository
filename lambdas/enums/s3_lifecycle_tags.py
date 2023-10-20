from enum import Enum


class S3LifecycleTags(Enum):
    SOFT_DELETE_KEY = "soft-delete"
    SOFT_DELETE_VAL = "true"
    DEATH_DELETE_KEY = "patient-death"
    DEATH_DELETE_VAL = "true"


print(S3LifecycleTags.SOFT_DELETE_KEY.value)
