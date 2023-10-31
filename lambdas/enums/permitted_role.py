from enum import Enum

class PermittedRole(Enum):
    GP = "RO76" 
    # DEV = "RO198" // Nope

    @staticmethod
    def list():
        return [org.value for org in list(PermittedRole)]
