from enum import Enum


class PermittedRole(Enum):
    PCSE = "RO157"
    GP_ADMIN = "RO76"
    GP_CLINICAL = "R8000"
    DEV = "RO198"

    @staticmethod
    def list():
        return [org.value for org in list(PermittedRole)]
