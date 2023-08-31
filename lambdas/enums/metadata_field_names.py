from enum import Enum


class DynamoField(Enum):
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
            DynamoField.ID,
            DynamoField.CONTENT_TYPE,
            DynamoField.CREATED,
            DynamoField.DOCUMENT_UPLOADED,
            DynamoField.FILE_NAME,
            DynamoField.INDEXED,
            DynamoField.LOCATION,
            DynamoField.NHS_NUMBER,
            DynamoField.TYPE,
            DynamoField.VIRUS_SCAN_RESULT,
        ]
