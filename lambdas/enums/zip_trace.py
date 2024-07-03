from enum import StrEnum


class ZipTraceFields(StrEnum):
    ID = "ID"
    JOB_ID = "JobId"
    CREATED = "Created"
    STATUS = "Status"
    ZIP_FILE_LOCATION = "ZipFileLocation"
    FILES_TO_DOWNLOAD = "FilesToDownload"


class ZipTraceStatus(StrEnum):
    PENDING = "Pending"
    COMPLETED = "Completed"
    PROCESSING = "Processing"
