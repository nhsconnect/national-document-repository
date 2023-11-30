import os

from enums.s3_lifecycle_tags import S3LifecycleTags
from enums.supported_document_types import SupportedDocumentTypes
from models.document_reference import DocumentReference
from services.document_service import DocumentService
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class DocumentDeletionService:
    def __init__(self):
        super().__init__()
        self.document_service = DocumentService()

    def handle_delete(self, nhs_number: str, doc_type: str) -> list[DocumentReference]:
        files_deleted = []
        match doc_type:
            case SupportedDocumentTypes.ALL.value:
                arf_deleted = self.handle_delete_for_doc_type(
                    nhs_number, str(SupportedDocumentTypes.ARF.value)
                )
                lg_deleted = self.handle_delete_for_doc_type(
                    nhs_number, str(SupportedDocumentTypes.LG.value)
                )
                files_deleted = arf_deleted + lg_deleted
            case SupportedDocumentTypes.ARF.value:
                files_deleted = self.handle_delete_for_doc_type(
                    nhs_number, str(SupportedDocumentTypes.ARF.value)
                )
            case SupportedDocumentTypes.LG.value:
                files_deleted = self.handle_delete_for_doc_type(
                    nhs_number, str(SupportedDocumentTypes.LG.value)
                )
        return files_deleted

    def handle_delete_for_doc_type(
        self, nhs_number: str, doc_type: str
    ) -> list[DocumentReference]:
        table_name = ""
        if doc_type == SupportedDocumentTypes.ARF.value:
            table_name = os.environ["DOCUMENT_STORE_DYNAMODB_NAME"]
        if doc_type == SupportedDocumentTypes.LG.value:
            table_name = os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]

        results = self.document_service.fetch_available_document_references_by_type(
            nhs_number, doc_type
        )

        if not results:
            return []

        self.document_service.delete_documents(
            table_name=table_name,
            document_references=results,
            type_of_delete=str(S3LifecycleTags.SOFT_DELETE.value),
        )
        logger.info(
            "Documents were deleted successfully", {"Result": "Successful deletion"}
        )
        return results
