from enum import Enum


class VirusScanResult(Enum):
    CLEAN = "Clean"
    INFECTED = "Infected"
    INFECTED_ALLOWED = "InfectedAllowed"
    UNSCANNABLE = "Unscannable"
    ERROR = "Error"


SCAN_RESULT_TAG_KEY = "scan-result"
