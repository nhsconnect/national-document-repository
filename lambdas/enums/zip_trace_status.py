from enum import StrEnum


class ZipTraceStatus(StrEnum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    PROCESSING = "PROCESSING"
