from enum import Enum
from typing import List


class RepositoryRole(Enum):
    GP_ADMIN = "GP_ADMIN"
    GP_CLINICAL = "GP_CLINICAL"
    PCSE = "PCSE"
    NONE = "NONE"

    @staticmethod
    def list() -> List[str]:
        return [str(item.value) for item in RepositoryRole]
