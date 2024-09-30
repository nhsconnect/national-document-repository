from enum import StrEnum


class MetadataReport(StrEnum):
    NhsNumber = "NhsNumber"
    UploadStatus = "UploadStatus"
    FailureReason = "FailureReason"
    PdsOdsCode = "PdsOdsCode"
    UploaderOdsCode = "UploaderOdsCode"
    FilePath = "FilePath"
    Date = "Date"
    Timestamp = "Timestamp"
    ID = "ID"

    @staticmethod
    def list():
        return [str(field) for field in MetadataReport]
