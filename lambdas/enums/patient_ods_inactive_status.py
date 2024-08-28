from enum import StrEnum


class PatientOdsInactiveStatus(StrEnum):
    SUSPENDED = "SUSP"
    DECEASED = "DECE"

    @staticmethod
    def list():
        return list(PatientOdsInactiveStatus.__members__.values())
