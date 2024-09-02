from enum import StrEnum


class PatientOdsInactiveStatus(StrEnum):
    SUSPENDED = "SUSP"
    DECEASED = "DECE"

    @staticmethod
    def list() -> list[str]:
        return list(PatientOdsInactiveStatus.__members__.values())
