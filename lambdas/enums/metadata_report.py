from enum import StrEnum


class MetadataReport(StrEnum):
    NhsNumber = "NhsNumber"
    UploadStatus = "UploadStatus"
    Reason = "Reason"
    PdsOdsCode = "PdsOdsCode"
    UploaderOdsCode = "UploaderOdsCode"
    FilePath = "FilePath"
    Date = "Date"
    Timestamp = "Timestamp"
    ID = "ID"
    RegisteredAtUploaderPractice = "RegisteredAtUploaderPractice"
