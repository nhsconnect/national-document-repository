from enum import Enum


class PermittedSmartRole(Enum):
    GP_ADMIN = "R8013"
    GP_CLINICAL = "R8000"
    PCSE = "R8015"

    @staticmethod
    def list():
        return [org.value for org in list(PermittedSmartRole)]
