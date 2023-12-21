from datetime import datetime, timezone

from enums.metadata_field_names import DocumentReferenceMetadataFields
from enums.s3_lifecycle_tags import S3LifecycleDays, S3LifecycleTags
from enums.supported_document_types import SupportedDocumentTypes
from models.document_reference import DocumentReference
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class DocumentService:
    def __init__(self):
        self.s3_service = S3Service()
        self.dynamo_service = DynamoDBService()

    def fetch_available_document_references_by_type(
        self, nhs_number: str, doc_type: SupportedDocumentTypes
    ) -> list[DocumentReference]:
        results: list[DocumentReference] = []
        delete_filter = {DocumentReferenceMetadataFields.DELETED.value: ""}

        doc_type_table = doc_type.get_dynamodb_table_name()
        if isinstance(doc_type_table, list):
            for table in doc_type_table:
                results += self.fetch_documents_from_table_with_filter(
                    nhs_number, table, attr_filter=delete_filter
                )
            return results

        return self.fetch_documents_from_table_with_filter(
            nhs_number, doc_type_table, attr_filter=delete_filter
        )

    def fetch_documents_from_table(
        self, nhs_number: str, table: str
    ) -> list[DocumentReference]:
        documents = []
        response = self.dynamo_service.query_with_requested_fields(
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

        response = self.dynamo_service.query_with_requested_fields(
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

            self.dynamo_service.update_item(
                table_name, reference.id, updated_fields=update_fields
            )
