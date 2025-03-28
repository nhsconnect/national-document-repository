from enum import StrEnum


class TraceStatus(StrEnum):
    PENDING = "Pending"
    COMPLETED = "Completed"
    PROCESSING = "Processing"
    FAILED = "Failed"
