import logging
import os
from datetime import datetime, timezone

from enums.metadata_field_names import DocumentReferenceMetadataFields
from enums.s3_lifecycle_tags import S3LifecycleTags
from enums.supported_document_types import SupportedDocumentTypes
from models.document_reference import DocumentReference
from services.dynamo_service import DynamoDBService
from services.s3_service import S3Service

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class DocumentService(DynamoDBService):
    def __init__(self):
        super().__init__()
        self.s3_service = S3Service()

    def retrieve_all_document_references(
        self, nhs_number: str, doc_types: str
    ) -> list[DocumentReference]:
        arf_documents = []
        lg_documents = []

        if SupportedDocumentTypes.ARF.name in doc_types:
            logger.info("Retrieving ARF documents")
            arf_documents = self.fetch_documents_from_table(
                nhs_number, os.environ["DOCUMENT_STORE_DYNAMODB_NAME"]
            )
        if SupportedDocumentTypes.LG.name in doc_types:
            logger.info("Retrieving Lloyd George documents")
            lg_documents = self.fetch_documents_from_table(
                nhs_number, os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]
            )

        return arf_documents + lg_documents

    def fetch_documents_from_table(
        self, nhs_number: str, table: str
    ) -> list[DocumentReference]:
        documents = []
        response = self.query_with_requested_fields(
            table_name=table,
            index_name="NhsNumberIndex",
            search_key="NhsNumber",
            search_condition=nhs_number,
            requested_fields=DocumentReferenceMetadataFields.list(),
        )

        for item in response["Items"]:
            document = DocumentReference.model_validate(item)
            documents.append(document)
        return documents

    def fetch_documents_from_table_with_filter(
        self, nhs_number: str, table: str, attr_filter: dict
    ) -> list[DocumentReference]:
        documents = []

        response = self.query_with_requested_fields(
            table_name=table,
            index_name="NhsNumberIndex",
            search_key="NhsNumber",
            search_condition=nhs_number,
            requested_fields=DocumentReferenceMetadataFields.list(),
            filtered_fields=attr_filter,
        )

        for item in response["Items"]:
            document = DocumentReference.model_validate(item)
            documents.append(document)
        return documents

    def delete_documents(self, table_name: str, documents: list[DocumentReference]):
        deletion_date = datetime.now(timezone.utc)

        ttl_days = float(S3LifecycleTags.SOFT_DELETE_DAYS.value)
        ttl_seconds = ttl_days * 24 * 60 * 60
        document_reference_ttl = int(deletion_date.timestamp() + ttl_seconds)

        update_fields = {
            DocumentReferenceMetadataFields.DELETED.value: deletion_date.strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            DocumentReferenceMetadataFields.TTL.value: document_reference_ttl,
        }

        logger.info(f"Deleting items in table: {table_name}")

        for doc in documents:
            self.s3_service.create_object_tag(
                file_key=doc.get_file_key(),
                s3_bucket_name=doc.get_file_bucket(),
                tag_key=str(S3LifecycleTags.SOFT_DELETE_KEY.value),
                tag_value=str(S3LifecycleTags.SOFT_DELETE_VAL.value),
            )

            self.update_item(table_name, doc.id, updated_fields=update_fields)
