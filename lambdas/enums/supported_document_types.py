import os
from enum import Enum
from typing import List

from enums.lambda_error import LambdaError
from utils.audit_logging_setup import LoggingService
from utils.lambda_exceptions import InvalidDocTypeException

logger = LoggingService(__name__)


class SupportedDocumentTypes(str, Enum):
    ARF = "ARF"
    LG = "LG"

    @staticmethod
    def list():
        return [SupportedDocumentTypes.ARF, SupportedDocumentTypes.LG]

    @staticmethod
    def list_names() -> List[str]:
        return [doc_type.value for doc_type in SupportedDocumentTypes.list()]

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

        try:
            document_type_to_table_name = {
                SupportedDocumentTypes.ARF: os.getenv("DOCUMENT_STORE_DYNAMODB_NAME"),
                SupportedDocumentTypes.LG: os.getenv("LLOYD_GEORGE_DYNAMODB_NAME"),
            }
            return document_type_to_table_name[self]
        except KeyError as e:
            logger.error(
                str(e),
                {
                    "Result": "An error occurred due to missing environment variable for doc_type"
                },
            )
            raise InvalidDocTypeException(status_code=500, error=LambdaError.DocTypeDB)
