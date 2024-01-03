import os

from enums.metadata_field_names import DocumentReferenceMetadataFields
from models.bulk_upload_status import FailedUpload, SuccessfulUpload
from models.nhs_document_reference import NHSDocumentReference
from models.staging_metadata import StagingMetadata
from services.base.dynamo_service import DynamoDBService
from utils.audit_logging_setup import LoggingService

_logger = LoggingService(__name__)


class BulkUploadDynamoRepository:
    def __init__(self):
        self.bulk_upload_report_dynamo_table = os.environ["BULK_UPLOAD_DYNAMODB_NAME"]
        self.lg_dynamo_table = os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]
        self.lg_bucket_name = os.environ["LLOYD_GEORGE_BUCKET_NAME"]

        self.dynamo_records_in_transaction: list[NHSDocumentReference] = []
        self.dynamo_repository = DynamoDBService()

    def create_record_in_lg_dynamo_table(
        self, document_reference: NHSDocumentReference
    ):
        self.dynamo_repository.create_item(
            table_name=self.lg_dynamo_table, item=document_reference.to_dict()
        )
        self.dynamo_records_in_transaction.append(document_reference)

    def report_upload_complete(self, staging_metadata: StagingMetadata):
        nhs_number = staging_metadata.nhs_number
        for file in staging_metadata.files:
            dynamo_record = SuccessfulUpload(
                nhs_number=nhs_number,
                file_path=file.file_path,
            )
            self.dynamo_repository.create_item(
                table_name=self.bulk_upload_report_dynamo_table,
                item=dynamo_record.model_dump(by_alias=True),
            )

    def report_upload_failure(
        self, staging_metadata: StagingMetadata, failure_reason: str
    ):
        nhs_number = staging_metadata.nhs_number

        for file in staging_metadata.files:
            dynamo_record = FailedUpload(
                nhs_number=nhs_number,
                failure_reason=failure_reason,
                file_path=file.file_path,
            )
            self.dynamo_repository.create_item(
                table_name=self.bulk_upload_report_dynamo_table,
                item=dynamo_record.model_dump(by_alias=True),
            )

    def init_transaction(self):
        self.dynamo_records_in_transaction = []

    def rollback_transaction(self):
        for document_reference in self.dynamo_records_in_transaction:
            primary_key_name = DocumentReferenceMetadataFields.ID.value
            primary_key_value = document_reference.id
            deletion_key = {primary_key_name: primary_key_value}
            self.dynamo_repository.delete_item(
                table_name=self.lg_dynamo_table, key=deletion_key
            )
