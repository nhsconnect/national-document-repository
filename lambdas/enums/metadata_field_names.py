from enum import Enum


class DocumentReferenceMetadataFields(Enum):
    ID = "ID"
    CONTENT_TYPE = "ContentType"
    CREATED = "Created"
    DELETED = "Deleted"
    FILE_NAME = "FileName"
    FILE_LOCATION = "FileLocation"
    NHS_NUMBER = "NhsNumber"
    TTL = "TTL"
    TYPE = "Type"
    VIRUS_SCANNER_RESULT = "VirusScannerResult"
    CURRENT_GP_ODS = "CurrentGpOds"

    @staticmethod
    def list() -> list[str]:
        return [str(field.value) for field in DocumentReferenceMetadataFields]


class DocumentZipTraceFields(Enum):
    ID = "ID"
    CREATED = "Created"
    FILE_LOCATION = "FileLocation"
