from enum import Enum, StrEnum
from typing import List


class RepositoryRole(Enum):
    GP_ADMIN = "GP_ADMIN"
    GP_CLINICAL = "GP_CLINICAL"
    PCSE = "PCSE"
    NONE = "NONE"

    @staticmethod
    def list() -> List[str]:
        return [str(item.value) for item in RepositoryRole]


class OrganisationRelationship(StrEnum):
    COMMISSIONED_BY = "RE4"
    CLINICAL_COMMISSIONING_GROUP = "RO98"
