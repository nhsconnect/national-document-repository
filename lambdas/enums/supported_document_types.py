import os
from enum import Enum
from typing import List

from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class SupportedDocumentTypes(str, Enum):
    ARF = "ARF"
    LG = "LG"

    @staticmethod
    def list():
        return [SupportedDocumentTypes.ARF, SupportedDocumentTypes.LG]

    @staticmethod
    def list_names() -> List[str]:
        return [str(doc_type.value) for doc_type in SupportedDocumentTypes.list()]

    def get_dynamodb_table_name(self) -> str:
        """
        Get the dynamodb table name related to a specific doc_type

        example usage:
            SupportedDocumentTypes.ARF.get_dynamodb_table_name()
            (returns "ndr*_DocumentReferenceMetadata")

        result:
            "ndr*_DocumentReferenceMetadata"

        Eventually we could replace all os.environ["XXX_DYNAMODB_NAME"] calls with this method,
        so that the logic of resolving table names are controlled in one place.
        """

        document_type_to_table_name = {
            SupportedDocumentTypes.ARF: os.getenv("DOCUMENT_STORE_DYNAMODB_NAME"),
            SupportedDocumentTypes.LG: os.getenv("LLOYD_GEORGE_DYNAMODB_NAME"),
        }
        return document_type_to_table_name[self]

    def get_s3_bucket_name(self) -> str:
        lookup_dict = {
            SupportedDocumentTypes.ARF: os.getenv("DOCUMENT_STORE_BUCKET_NAME"),
            SupportedDocumentTypes.LG: os.getenv("LLOYD_GEORGE_BUCKET_NAME"),
        }
        return lookup_dict[self]
