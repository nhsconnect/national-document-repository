from enum import Enum


class PermittedRole(Enum):
    PCSE = "RO157"
    GP = "RO76"
    DEV = "RO198"

    @staticmethod
    def list():
        return [org.value for org in list(PermittedRole)]
