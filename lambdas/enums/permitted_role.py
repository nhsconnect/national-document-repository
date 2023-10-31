from enum import Enum


// User Role Codes
class PermittedRole(Enum):
    GP = "RO76" // role_code_gpp_org

    # DEV = "RO198" // Nope

    @staticmethod
    def list():
        return [org.value for org in list(PermittedRole)]
