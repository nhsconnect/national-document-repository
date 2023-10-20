from enum import Enum


class DocumentReferenceMetadataFields(Enum):
    ID = "ID", "#id"
    CONTENT_TYPE = "ContentType", "#contentType"
    CREATED = "Created", "#created"
    DELETED = "Deleted", "#deleted"
    FILE_NAME = "FileName", "#fileName"
    FILE_LOCATION = "FileLocation", "#fileLocation"
    NHS_NUMBER = "NhsNumber", "#nhsNumber"
    TYPE = "Type", "#type"
    VIRUS_SCANNER_RESULT = "VirusScannerResult", "#vscanResult"

    def __init__(self, field_name, field_alias):
        self.field_name = field_name
        self.field_alias = field_alias

    @staticmethod
    def list():
        return [
            DocumentReferenceMetadataFields.ID,
            DocumentReferenceMetadataFields.CONTENT_TYPE,
            DocumentReferenceMetadataFields.CREATED,
            DocumentReferenceMetadataFields.DELETED,
            DocumentReferenceMetadataFields.FILE_NAME,
            DocumentReferenceMetadataFields.FILE_LOCATION,
            DocumentReferenceMetadataFields.NHS_NUMBER,
            DocumentReferenceMetadataFields.TYPE,
            DocumentReferenceMetadataFields.VIRUS_SCANNER_RESULT,
        ]


class DocumentZipTraceFields(Enum):
    ID = "ID"
    CREATED = "Created"
    FILE_LOCATION = "FileLocation"
