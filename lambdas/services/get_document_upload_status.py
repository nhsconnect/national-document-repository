from enums.document_status import DocumentStatus
from enums.supported_document_types import SupportedDocumentTypes
from enums.virus_scan_result import VirusScanResult
from services.document_service import DocumentService
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class GetDocumentUploadStatusService:
    def __init__(self):
        self.document_service = DocumentService()

    def _determine_document_status(self, doc_ref, nhs_number):
        if not doc_ref:
            return DocumentStatus.NOT_FOUND.display, DocumentStatus.NOT_FOUND.code

        if doc_ref.nhs_number != nhs_number:
            return DocumentStatus.FORBIDDEN.display, DocumentStatus.FORBIDDEN.code

        if doc_ref.deleted:
            return None, None

        if doc_ref.doc_status == "cancelled":
            if doc_ref.virus_scanner_result == VirusScanResult.INFECTED:
                return DocumentStatus.INFECTED.display, DocumentStatus.INFECTED.code
            return DocumentStatus.CANCELLED.display, DocumentStatus.CANCELLED.code

        return doc_ref.doc_status, None

    def get_document_references_by_id(
        self, nhs_number: str, document_ids: list[str]
    ) -> dict:
        """
        Checks the status of a list of documents for a given patient.

        Args:
            nhs_number: The NHS number of the patient.
            document_ids: A list of document IDs to check.

        Returns:
            A dictionary with a list of document IDs and their corresponding statuses.
        """
        found_docs = self.document_service.get_batch_document_references_by_id(
            document_ids, SupportedDocumentTypes.LG
        )
        found_docs_by_id = {doc.id: doc for doc in found_docs}
        results = {}

        for doc_id in document_ids:
            doc_ref = found_docs_by_id.get(doc_id)
            status, error_code = self._determine_document_status(doc_ref, nhs_number)

            if status is None:
                continue

            result = {"status": status}
            if error_code:
                result["error_code"] = error_code
            results[doc_id] = result

        return results
