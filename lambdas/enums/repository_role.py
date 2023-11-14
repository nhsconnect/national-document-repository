from enum import Enum


class RepositoryRole(Enum):
    GP_ADMIN = "GP_ADMIN"
    GP_CLINICAL = "GP_CLINICAL"
    PCSE = "PCSE"
    NONE = "NONE"

    @staticmethod
    def list():
        return tuple(item.value for item in RepositoryRole)
