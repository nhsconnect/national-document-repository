from enum import Enum


class DynamoDocumentMetadataTableFields(Enum):
    ID = "ID", "#id"
    CONTENT_TYPE = "ContentType", "#contentType"
    CREATED = "Created", "#created"
    DOCUMENT_UPLOADED = "DocumentUploaded", "#docUploaded"
    FILE_NAME = "FileName", "#fileName"
    INDEXED = "Indexed", "#indexed"
    LOCATION = "Location", "#location"
    NHS_NUMBER = "NhsNumber", "#nhsNumber"
    TYPE = "Type", "#type"
    VIRUS_SCAN_RESULT = "VirusScanResult", "#vscanResult"

    def __init__(self, field_name, field_alias):
        self.field_name = field_name
        self.field_alias = field_alias

    @staticmethod
    def list():
        return [
            DynamoDocumentMetadataTableFields.ID,
            DynamoDocumentMetadataTableFields.CONTENT_TYPE,
            DynamoDocumentMetadataTableFields.CREATED,
            DynamoDocumentMetadataTableFields.DOCUMENT_UPLOADED,
            DynamoDocumentMetadataTableFields.FILE_NAME,
            DynamoDocumentMetadataTableFields.INDEXED,
            DynamoDocumentMetadataTableFields.LOCATION,
            DynamoDocumentMetadataTableFields.NHS_NUMBER,
            DynamoDocumentMetadataTableFields.TYPE,
            DynamoDocumentMetadataTableFields.VIRUS_SCAN_RESULT,
        ]
