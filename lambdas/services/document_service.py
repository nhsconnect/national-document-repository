import os
from datetime import datetime, timezone

from enums.metadata_field_names import DocumentReferenceMetadataFields
from enums.s3_lifecycle_tags import S3LifecycleDays, S3LifecycleTags
from enums.supported_document_types import SupportedDocumentTypes
from models.document_reference import DocumentReference
from services.dynamo_service import DynamoDBService
from services.s3_service import S3Service
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class DocumentService(DynamoDBService):
    def __init__(self):
        super().__init__()
        self.s3_service = S3Service()

    def fetch_available_document_references_by_type(
        self, nhs_number: str, doc_type: str
    ) -> list[DocumentReference]:
        results: list[DocumentReference] = []
        delete_filter = {DocumentReferenceMetadataFields.DELETED.value: ""}

        if doc_type == SupportedDocumentTypes.ALL.value:
            results = self.fetch_documents_from_table_with_filter(
                nhs_number,
                os.environ["DOCUMENT_STORE_DYNAMODB_NAME"],
                attr_filter=delete_filter,
            ) + self.fetch_documents_from_table_with_filter(
                nhs_number,
                os.environ["LLOYD_GEORGE_DYNAMODB_NAME"],
                attr_filter=delete_filter,
            )

        if doc_type == SupportedDocumentTypes.ARF.value:
            results = self.fetch_documents_from_table_with_filter(
                nhs_number,
                os.environ["DOCUMENT_STORE_DYNAMODB_NAME"],
                attr_filter=delete_filter,
            )

        if doc_type == SupportedDocumentTypes.LG.value:
            results = self.fetch_documents_from_table_with_filter(
                nhs_number,
                os.environ["LLOYD_GEORGE_DYNAMODB_NAME"],
                attr_filter=delete_filter,
            )
        return results

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

    def delete_documents(
        self,
        table_name: str,
        document_references: list[DocumentReference],
        type_of_delete: str,
    ):
        deletion_date = datetime.now(timezone.utc)

        if type_of_delete == S3LifecycleTags.DEATH_DELETE.value:
            ttl_days = S3LifecycleDays.DEATH_DELETE
            tag_key = str(S3LifecycleTags.DEATH_DELETE.value)
        else:
            ttl_days = S3LifecycleDays.SOFT_DELETE
            tag_key = str(S3LifecycleTags.SOFT_DELETE.value)

        ttl_seconds = ttl_days * 24 * 60 * 60
        document_reference_ttl = int(deletion_date.timestamp() + ttl_seconds)

        update_fields = {
            DocumentReferenceMetadataFields.DELETED.value: deletion_date.strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            DocumentReferenceMetadataFields.TTL.value: document_reference_ttl,
        }

        logger.info(f"Deleting items in table: {table_name}")

        for reference in document_references:
            self.s3_service.create_object_tag(
                file_key=reference.get_file_key(),
                s3_bucket_name=reference.get_file_bucket(),
                tag_key=tag_key,
                tag_value=str(S3LifecycleTags.ENABLE_TAG.value),
            )

            self.update_item(table_name, reference.id, updated_fields=update_fields)

    def delete_documents_by_type(
        self,
        doc_type: str,
        document_references: list[DocumentReference],
        type_of_delete: str,
    ):
        if doc_type == SupportedDocumentTypes.ARF.value:
            table_name = os.environ["DOCUMENT_STORE_DYNAMODB_NAME"]
        elif doc_type == SupportedDocumentTypes.LG.value:
            table_name = os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]
        else:
            raise ValueError("Unsupported doc type")

        return self.delete_documents(
            table_name=table_name,
            document_references=document_references,
            type_of_delete=type_of_delete,
        )
