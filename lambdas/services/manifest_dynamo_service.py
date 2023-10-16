import logging
import os

from enums.supported_document_types import SupportedDocumentTypes
from services.dynamo_service import DynamoDBService
from enums.metadata_field_names import DocumentReferenceMetadataFields
from models.document import Document
from utils.exceptions import DynamoDbException

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class ManifestDynamoService(DynamoDBService):

    def discover_uploaded_documents(
            self, nhs_number: str, doc_types: str
    ) -> list[Document]:
        arf_documents = []
        lg_documents = []

        if SupportedDocumentTypes.ARF.name in doc_types:
            arf_documents = self.fetch_documents_from_table(nhs_number, os.environ["DOCUMENT_STORE_DYNAMODB_NAME"])
        if SupportedDocumentTypes.LG.name in doc_types:
            lg_documents = self.fetch_documents_from_table(nhs_number, os.environ["LLOYD_GEORGE_DYNAMODB_NAME"])

        return arf_documents + lg_documents

    def fetch_documents_from_table(self, nhs_number: str, table: str) -> list[Document]:
        documents = []
        response = self.query_service(
            table,
            "NhsNumberIndex",
            "NhsNumber",
            nhs_number,
            [
                DocumentReferenceMetadataFields.FILE_NAME,
                DocumentReferenceMetadataFields.FILE_LOCATION,
                DocumentReferenceMetadataFields.VIRUS_SCAN_RESULT,
            ],
        )

        for item in response["Items"]:
            document = Document(
                nhs_number=nhs_number,
                file_name=item[DocumentReferenceMetadataFields.FILE_NAME.field_name],
                virus_scanner_result=item[
                    DocumentReferenceMetadataFields.VIRUS_SCAN_RESULT.field_name
                ],
                file_location=item[
                    DocumentReferenceMetadataFields.FILE_LOCATION.field_name
                ],
            )
            documents.append(document)
        return documents
