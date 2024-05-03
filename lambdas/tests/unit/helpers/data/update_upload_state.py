import json

from enums.metadata_field_names import DocumentReferenceMetadataFields
from enums.supported_document_types import SupportedDocumentTypes
from tests.unit.conftest import TEST_FILE_KEY

Fields = DocumentReferenceMetadataFields

MOCK_DOCUMENT_REFERENCE = TEST_FILE_KEY

MOCK_LG_DOCUMENTS_REQUEST = {
    "files": [
        {
            "reference": TEST_FILE_KEY,
            "type": str(SupportedDocumentTypes.LG.value),
            "fields": {Fields.UPLOADING.value: True},
        }
    ]
}

MOCK_ARF_DOCUMENTS_REQUEST = {
    "files": [
        {
            "reference": TEST_FILE_KEY,
            "type": str(SupportedDocumentTypes.ARF.value),
            "fields": {Fields.UPLOADING.value: True},
        }
    ]
}

MOCK_INVALID_TYPE_DOCUMENTS_REQUEST = {
    "files": [
        {
            "reference": TEST_FILE_KEY,
            "type": "INVALID_TYPE",
            "fields": {Fields.UPLOADING.value: True},
        }
    ]
}

MOCK_NO_DOCTYPE_REQUEST = {
    "files": [
        {
            "reference": TEST_FILE_KEY,
            "type": "",
            "fields": {Fields.UPLOADING.value: True},
        }
    ]
}
MOCK_NO_REFERENCE_REQUEST = {
    "files": [
        {
            "reference": TEST_FILE_KEY,
            "type": "",
            "fields": {Fields.UPLOADING.value: True},
        }
    ]
}

MOCK_NO_FIELDS_REQUEST = {
    "files": [
        {
            "reference": TEST_FILE_KEY,
            "type": "",
            "fields": {},
        }
    ]
}

MOCK_UPLOADING_FIELDS = {Fields.UPLOADING.value: True}

MOCK_NO_FILES_REQUEST = {"test": "test"}

MOCK_EMPTY_LIST = []

MOCK_VALID_LG_EVENT = {
    "httpMethod": "POST",
    "body": json.dumps(MOCK_LG_DOCUMENTS_REQUEST),
}

MOCK_VALID_ARF_EVENT = {
    "httpMethod": "POST",
    "body": json.dumps(MOCK_ARF_DOCUMENTS_REQUEST),
}

MOCK_INVALID_TYPE_EVENT = {
    "httpMethod": "POST",
    "body": json.dumps(MOCK_INVALID_TYPE_DOCUMENTS_REQUEST),
}

MOCK_INVALID_BODY_EVENT = {"httpMethod": "POST", "body": "test"}

MOCK_NO_BODY_EVENT = {"httpMethod": "POST", "test": "test"}
