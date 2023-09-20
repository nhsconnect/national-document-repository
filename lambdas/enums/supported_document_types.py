from enum import Enum

class SupportedDocumentTypes(Enum):
    ARF = "ARF", "#arf"
    LG = "LG", "#lg"

    def __init__(self, field_name, field_alias):
        self.field_name = field_name
        self.field_alias = field_alias

    @staticmethod
    def list():
        return [
            SupportedDocumentTypes.ARF,
            SupportedDocumentTypes.LG
        ]

    @staticmethod
    def list_names():
        return [
            SupportedDocumentTypes.ARF.name,
            SupportedDocumentTypes.LG.name
        ]