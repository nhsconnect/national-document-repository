from enum import StrEnum
from typing import Optional


class DeathNotificationStatus(StrEnum):
    INFORMAL = "INFORMAL"
    FORMAL = "FORMAL"
    REMOVED = "REMOVED"

    @staticmethod
    def from_code(code: str) -> Optional["DeathNotificationStatus"]:
        match code:
            case "1":
                return DeathNotificationStatus.INFORMAL
            case "2":
                return DeathNotificationStatus.FORMAL
            case "U":
                return DeathNotificationStatus.REMOVED
            case _:
                return None
