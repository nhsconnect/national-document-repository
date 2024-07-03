from enums.supported_document_types import SupportedDocumentTypes


def doc_type_is_valid(value: str) -> bool:
    if not len(extract_document_type_to_enum(value)):
        return False
    return True


def extract_document_type_to_enum(value: str) -> list[SupportedDocumentTypes]:
    received_document_types = value.replace(" ", "").split(",")
    converted_document_types = []
    for document_type in received_document_types:
        try:
            converted_document_types.append(SupportedDocumentTypes(document_type))
        except ValueError:
            continue
    return converted_document_types


def extract_single_document_type(value: str) -> SupportedDocumentTypes | None:
    received_document_type = value.replace(" ", "")
    for item in SupportedDocumentTypes:
        if item.value == received_document_type:
            return item
    return None
