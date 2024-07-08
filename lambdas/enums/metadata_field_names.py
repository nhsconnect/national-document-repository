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
    VIRUS_SCANNER_RESULT = "VirusScannerResult"
    CURRENT_GP_ODS = "CurrentGpOds"
    UPLOADED = "Uploaded"
    UPLOADING = "Uploading"
    LAST_UPDATED = "LastUpdated"

    @staticmethod
    def list() -> list[str]:
        fields = [str(field.value) for field in DocumentReferenceMetadataFields]
        fields.remove(DocumentReferenceMetadataFields.TTL.value)
        return fields
