from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, ValidationError


class ScanResult(StrEnum):
    CLEAN = "Clean"
    INFECTED = "Infected"
    NOT_SCANNED = "Not Scanned"
    SUSPICIOUS = "Suspicious"
    ERROR = "Error"
    UNSCANNABLE = "Unscannable"
    UNKNOWN = "Unknown"


class VirusScannedEvent(BaseModel):
    bucketName: str
    key: str
    result: ScanResult
