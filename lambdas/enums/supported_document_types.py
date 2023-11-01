from enum import Enum


class SupportedDocumentTypes(Enum):
    ARF = "ARF"
    LG = "LG"
    ALL = "ALL"

    @staticmethod
    def list():
        return [SupportedDocumentTypes.ARF, SupportedDocumentTypes.LG]

    @staticmethod
    def list_names() -> [str]:
        return [str(doc_type.value) for doc_type in SupportedDocumentTypes.list()]

    @staticmethod
    def get_from_field_name(value: str):
        if value in SupportedDocumentTypes.list_names():
            return value
        return None
