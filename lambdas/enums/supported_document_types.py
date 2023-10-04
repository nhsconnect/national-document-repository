from enum import Enum


class SupportedDocumentTypes(Enum):
    ARF = "ARF", "#arf"
    LG = "LG", "#lg"

    def __init__(self, field_name, field_alias):
        self.field_name = field_name
        self.field_alias = field_alias

    @staticmethod
    def list():
        return [SupportedDocumentTypes.ARF, SupportedDocumentTypes.LG]

    @staticmethod
    def list_names():
        return [SupportedDocumentTypes.ARF.name, SupportedDocumentTypes.LG.name]

    @staticmethod
    def get_from_field_name(enum_value):
        for supported_document_type in SupportedDocumentTypes.list():
            if supported_document_type.name == enum_value:
                return supported_document_type
        return None
