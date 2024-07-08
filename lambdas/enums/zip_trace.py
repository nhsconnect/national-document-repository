from enum import StrEnum


class ZipTraceStatus(StrEnum):
    PENDING = "Pending"
    COMPLETED = "Completed"
    PROCESSING = "Processing"
