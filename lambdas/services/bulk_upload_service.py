import logging
import os
import uuid
from urllib.parse import urlparse

from enums.metadata_field_names import DocumentReferenceMetadataFields
from models.nhs_document_reference import NHSDocumentReference
from models.staging_metadata import MetadataFile, StagingMetadata
from services.dynamo_service import DynamoDBService
from services.s3_service import S3Service
from services.sqs_service import SQSService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class BulkUploadService:
    def __init__(
        self,
    ):
        self.s3_service = S3Service()
        self.dynamo_service = DynamoDBService()
        self.sqs_service = SQSService()

        self.staging_bucket_name = os.environ["STAGING_STORE_BUCKET_NAME"]
        self.lg_bucket_name = os.environ["LLOYD_GEORGE_BUCKET_NAME"]
        self.lg_dynamo_table = os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]

        self.pdf_content_type = "application/pdf"
        self.dynamo_records_in_transaction: list[NHSDocumentReference] = []
        self.dest_bucket_files_in_transaction = []

    def handle_sqs_message(self, message: dict):
        if message["eventSource"] != "aws:sqs":
            logger.info("Rejecting message as not coming from sqs")
            raise RuntimeError()

        self.init_transaction()

        staging_metadata_json = message["body"]
        staging_metadata = StagingMetadata.model_validate_json(staging_metadata_json)
        [
            os.path.basename(metadata.file_path) for metadata in staging_metadata.files
        ]

        # validate lg_filenames here

        try:
            self.create_lg_records_and_copy_files(staging_metadata)
        except Exception as e:
            logger.error(e)
            self.undo_transaction()

    def init_transaction(self):
        self.dynamo_records_in_transaction = []
        self.dest_bucket_files_in_transaction = []

    def undo_transaction(self):
        for document_reference in self.dynamo_records_in_transaction:
            primary_key_name = DocumentReferenceMetadataFields.ID.field_name
            primary_key_value = document_reference.id
            deletion_key = {primary_key_name: primary_key_value}
            self.dynamo_service.delete_item(
                table_name=self.lg_dynamo_table, key=deletion_key
            )
        for dest_bucket_file_name in self.dest_bucket_files_in_transaction:
            pass
            # delete the copied file here

    def create_lg_records_and_copy_files(self, staging_metadata: StagingMetadata):
        nhs_number = staging_metadata.nhs_number

        for file_metadata in staging_metadata.files:
            document_reference = self.convert_to_document_reference(
                file_metadata, nhs_number
            )
            source_file_key = file_metadata.file_path
            dest_file_key = self.get_file_key_from_full_s3_path(
                document_reference.file_location
            )

            self.dynamo_service.post_item_service(
                self.lg_dynamo_table, document_reference.to_dict()
            )
            self.dynamo_records_in_transaction.append(document_reference)
            self.copy_to_lg_bucket(
                source_file_key=source_file_key, dest_file_key=dest_file_key
            )

    def copy_to_lg_bucket(self, source_file_key: str, dest_file_key: str):
        self.s3_service.copy_across_bucket(
            source_bucket=self.staging_bucket_name,
            source_file_key=source_file_key,
            dest_bucket=self.lg_bucket_name,
            dest_file_key=dest_file_key,
        )

    def convert_to_document_reference(
        self, file_metadata: MetadataFile, nhs_number: str
    ) -> NHSDocumentReference:
        reference_id = self.create_reference_id()
        file_name = os.path.basename(file_metadata.file_path)

        return NHSDocumentReference(
            nhs_number=nhs_number,
            content_type=self.pdf_content_type,
            file_name=file_name,
            reference_id=reference_id,
            s3_bucket_name=self.lg_bucket_name,
        )

    def get_file_key_from_full_s3_path(self, full_s3_path: str):
        return urlparse(full_s3_path).path.lstrip("/")

    @staticmethod
    def create_reference_id() -> str:
        return str(uuid.uuid4())
