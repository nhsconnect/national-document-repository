from enum import StrEnum


class VirusScanResult(StrEnum):
    CLEAN = "Clean"
    INFECTED = "Infected"
    INFECTED_ALLOWED = "InfectedAllowed"
    UNSCANNABLE = "Unscannable"
    ERROR = "Error"


SCAN_RESULT_TAG_KEY = "scan-result"
