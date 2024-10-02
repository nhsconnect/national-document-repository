from enum import StrEnum


class PatientOdsInactiveStatus(StrEnum):
    RESTRICTED = "REST"
    SUSPENDED = "SUSP"
    DECEASED = "DECE"

    @staticmethod
    def list() -> list[str]:
        return list(PatientOdsInactiveStatus.__members__.values())

    @staticmethod
    def str_list():
        return [str(field) for field in PatientOdsInactiveStatus]
