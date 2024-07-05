from enum import StrEnum


class ZipTraceFields(StrEnum):
    ID = "ID"
    JOB_ID = "JobId"
    CREATED = "Created"
    STATUS = "JobStatus"
    ZIP_FILE_LOCATION = "ZipFileLocation"
    FILES_TO_DOWNLOAD = "FilesToDownload"

    @staticmethod
    def list():
        return [
            ZipTraceFields.ID,
            ZipTraceFields.JOB_ID,
            ZipTraceFields.CREATED,
            ZipTraceFields.STATUS,
            ZipTraceFields.ZIP_FILE_LOCATION,
            ZipTraceFields.FILES_TO_DOWNLOAD,
        ]


class ZipTraceStatus(StrEnum):
    PENDING = "Pending"
    COMPLETED = "Completed"
    PROCESSING = "Processing"
