from enums.supported_document_types import SupportedDocumentTypes


def doc_type_is_valid(value: str) -> bool:
    if extract_document_type_to_enum(value) is None:
        return False
    return True


def extract_document_type_to_enum(value: str) -> SupportedDocumentTypes:
    doc_type = value.replace(" ", "")

    if doc_type == SupportedDocumentTypes.LG.value:
        return SupportedDocumentTypes.LG
    elif doc_type == SupportedDocumentTypes.ARF.value:
        return SupportedDocumentTypes.ARF
    elif set(doc_type.split(",")) == set(SupportedDocumentTypes.list_names()):
        return SupportedDocumentTypes.ALL
