from enums.metadata_field_names import DocumentReferenceMetadataFields
from enums.supported_document_types import SupportedDocumentTypes
from tests.unit.conftest import TEST_FILE_KEY

Fields = DocumentReferenceMetadataFields

MOCK_LG_DOCTYPE = SupportedDocumentTypes.LG.value
MOCK_LG_DOCUMENT_REFERENCE = TEST_FILE_KEY
MOCK_LG_DOCUMENTS_REQUEST = {
    "files": [
        {
            "reference": TEST_FILE_KEY,
            "type": SupportedDocumentTypes.LG.value,
            "fields": {Fields.UPLOADING.value: "true"},
        }
    ]
}

MOCK_ARF_DOCTYPE = SupportedDocumentTypes.ARF.value
MOCK_ARF_DOCUMENT_REFERENCE = TEST_FILE_KEY
MOCK_ARF_DOCUMENTS_REQUEST = {
    "files": [
        {
            "reference": TEST_FILE_KEY,
            "type": SupportedDocumentTypes.ARF.value,
            "fields": {Fields.UPLOADING.value: "true"},
        }
    ]
}
