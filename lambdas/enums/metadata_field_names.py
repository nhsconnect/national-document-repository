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

    @staticmethod
    def list() -> list[str]:
        return [
            DocumentReferenceMetadataFields.ID.value,
            DocumentReferenceMetadataFields.CONTENT_TYPE.value,
            DocumentReferenceMetadataFields.CREATED.value,
            DocumentReferenceMetadataFields.DELETED.value,
            DocumentReferenceMetadataFields.FILE_NAME.value,
            DocumentReferenceMetadataFields.FILE_LOCATION.value,
            DocumentReferenceMetadataFields.NHS_NUMBER.value,
            DocumentReferenceMetadataFields.TTL.value,
            DocumentReferenceMetadataFields.TYPE.value,
            DocumentReferenceMetadataFields.VIRUS_SCANNER_RESULT.value,
        ]


class DocumentZipTraceFields(Enum):
    ID = "ID"
    CREATED = "Created"
    FILE_LOCATION = "FileLocation"
