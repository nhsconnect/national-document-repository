from datetime import datetime, timezone

from boto3.dynamodb.conditions import Attr, ConditionBase
from enums.metadata_field_names import DocumentReferenceMetadataFields
from enums.supported_document_types import SupportedDocumentTypes
from models.document_reference import DocumentReference
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from utils.audit_logging_setup import LoggingService
from utils.dynamo_utils import filter_uploaded_docs_and_recently_uploading_docs
from utils.exceptions import (
    DocumentServiceException,
    FileUploadInProgress,
    NoAvailableDocument,
)

logger = LoggingService(__name__)


class DocumentService:
    def __init__(self):
        self.s3_service = S3Service()
        self.dynamo_service = DynamoDBService()

    def fetch_available_document_references_by_type(
        self,
        nhs_number: str,
        doc_type: SupportedDocumentTypes,
        query_filter: Attr | ConditionBase,
    ) -> list[DocumentReference]:
        table_name = doc_type.get_dynamodb_table_name()

        return self.fetch_documents_from_table_with_filter(
            nhs_number, table_name, query_filter=query_filter
        )

    def fetch_documents_from_table(
        self, nhs_number: str, table: str
    ) -> list[DocumentReference]:
        documents = []
        response = self.dynamo_service.query_table_by_index(
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
        self, nhs_number: str, table: str, query_filter: Attr | ConditionBase
    ) -> list[DocumentReference]:
        documents = []

        response = self.dynamo_service.query_table_by_index(
            table_name=table,
            index_name="NhsNumberIndex",
            search_key="NhsNumber",
            search_condition=nhs_number,
            requested_fields=DocumentReferenceMetadataFields.list(),
            query_filter=query_filter,
        )

        for item in response["Items"]:
            document = DocumentReference.model_validate(item)
            documents.append(document)
        return documents

    def delete_document_references(
        self,
        table_name: str,
        document_references: list[DocumentReference],
        document_ttl_days: int,
    ):
        deletion_date = datetime.now(timezone.utc)

        ttl_seconds = document_ttl_days * 24 * 60 * 60
        document_reference_ttl = int(deletion_date.timestamp() + ttl_seconds)

        update_fields = {
            DocumentReferenceMetadataFields.DELETED.value: deletion_date.strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            DocumentReferenceMetadataFields.TTL.value: document_reference_ttl,
        }

        logger.info(f"Deleting items in table: {table_name}")

        for reference in document_references:
            self.dynamo_service.update_item(
                table_name, reference.id, updated_fields=update_fields
            )

    def delete_document_object(self, bucket: str, key: str):
        file_exists = self.s3_service.file_exist_on_s3(
            s3_bucket_name=bucket, file_key=key
        )

        if not file_exists:
            raise DocumentServiceException("Document does not exist in S3")

        logger.info(
            f"Located file `{key}` in `{bucket}`, attempting S3 object deletion"
        )
        self.s3_service.delete_object(s3_bucket_name=bucket, file_key=key)

        file_exists = self.s3_service.file_exist_on_s3(
            s3_bucket_name=bucket, file_key=key
        )

        if file_exists:
            raise DocumentServiceException("Document located in S3 after deletion")

    def update_documents(
        self,
        table_name: str,
        document_references: list[DocumentReference],
        update_fields: dict,
    ):
        for reference in document_references:
            self.dynamo_service.update_item(
                table_name, reference.id, updated_fields=update_fields
            )

    def hard_delete_metadata_records(
        self, table_name: str, document_references: list[DocumentReference]
    ):
        logger.info(f"Deleting items in table: {table_name} (HARD DELETE)")
        primary_key_name = DocumentReferenceMetadataFields.ID.value
        for reference in document_references:
            primary_key_value = reference.id
            deletion_key = {primary_key_name: primary_key_value}
            self.dynamo_service.delete_item(table_name, deletion_key)

    @staticmethod
    def is_upload_in_process(records: list[DocumentReference]):
        return any(
            not record.uploaded
            and record.uploading
            and record.last_updated_within_three_minutes()
            for record in records
        )

    def get_available_lloyd_george_record_for_patient(
        self, nhs_number
    ) -> list[DocumentReference]:
        filter_expression = filter_uploaded_docs_and_recently_uploading_docs()
        available_docs = self.fetch_available_document_references_by_type(
            nhs_number,
            SupportedDocumentTypes.LG,
            query_filter=filter_expression,
        )

        file_in_progress_message = (
            "The patients Lloyd George record is in the process of being uploaded"
        )
        if not available_docs:
            raise NoAvailableDocument()
        for document in available_docs:
            if document.uploading and not document.uploaded:
                raise FileUploadInProgress(file_in_progress_message)
        return available_docs
